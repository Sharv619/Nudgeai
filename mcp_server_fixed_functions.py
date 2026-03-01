    @server.tool(
        name="query_codebase",
        description="Search and analyze the local codebase for optimization opportunities",
        title="Codebase Analysis Tool",
    )
    async def query_codebase(
        query: str, file_type: Optional[str] = None, max_results: int = 5
    ) -> Dict[str, Any]:
        """
        Search through the local codebase based on a query and process with Hugging Face model.
        This tool analyzes code files in the current project to identify optimization opportunities.

        Args:
            query: Search query string (e.g., 'optimization', 'performance', 'refactoring')
            file_type: Optional filter for file type (e.g., 'py', 'js', 'ts')
            max_results: Maximum number of results to return (default 5)

        Returns:
            Dictionary with matching code segments and AI-processed analysis
        """
        logger.info(
            f"Searching codebase for: '{query}', type: {file_type}, max: {max_results}"
        )

        # Import the codebase ingestion modules
        from data_ingestion.codebase.code_fetcher import CodeFetcher
        
        # Initialize the code fetcher
        fetcher = CodeFetcher()
        
        # Define supported file extensions
        if file_type:
            extensions = [f".{file_type}"]
        else:
            extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.html', '.css', '.md']
        
        # Fetch code files from the project
        code_files = fetcher.fetch_files(extensions)
        
        # Filter and sort files based on relevance to the query
        filtered_files = []
        for file_info in code_files:
            # Look for the query term in filename or content
            if query.lower() in file_info['filename'].lower() or query.lower() in file_info['content'].lower():
                filtered_files.append(file_info)
        
        # Sort by size and take top results
        filtered_files = sorted(filtered_files, key=lambda x: x['size'], reverse=True)[:max_results]
        
        # Process the code content with Hugging Face model to generate analysis
        if filtered_files:
            code_context = "\n".join([
                f"File: {f['path']}\nContent Preview: {f['content'][:300]}...\n" 
                for f in filtered_files
            ])
            prompt = f"""
            Analyze the following codebase files in response to the query '{query}':
            {code_context}
            
            Provide a concise analysis of the code and specific suggestions for:
            1. Optimization opportunities
            2. Performance improvements
            3. Code quality enhancements
            4. Best practices recommendations
            """
        else:
            # If no files match the query, search for files more broadly
            all_files = sorted(code_files, key=lambda x: x['size'], reverse=True)[:max_results]
            if all_files:
                code_context = "\n".join([
                    f"File: {f['path']}\nContent Preview: {f['content'][:200]}...\n" 
                    for f in all_files
                ])
                prompt = f"""
                Here are some codebase files. Analyze them in light of the query '{query}':
                {code_context}
                
                Provide a concise analysis of the code and specific suggestions for:
                1. Performance improvements
                2. Code quality enhancements
                3. Best practices recommendations
                """
                filtered_files = all_files
            else:
                prompt = f"No code files were found in the project to analyze for the query '{query}'."

        ai_analysis = _process_with_hf_model(prompt)

        # Prepare simplified file info for response
        result_files = []
        if filtered_files:  # Only process if filtered_files is not empty
            result_files = [
                {
                    'path': f['path'],
                    'filename': f['filename'],
                    'size': f['size'],
                    'lines': f['lines']
                } for f in filtered_files
            ]

        return {
            "files": result_files, 
            "analysis": ai_analysis, 
            "count": len(result_files),
            "query": query
        }

    @server.tool(
        name="analyze_codebase_patterns",
        description="Identify patterns in the codebase that may indicate optimization opportunities",
        title="Code Pattern Analysis Tool",
    )
    async def analyze_codebase_patterns() -> Dict[str, Any]:
        """
        Analyze the codebase to identify patterns that may indicate optimization opportunities.
        Looks for common patterns like repeated code, inefficient algorithms, etc.

        Returns:
            Analysis of codebase patterns with optimization suggestions
        """
        logger.info("Analyzing codebase patterns for optimization opportunities")
        
        # Import the codebase ingestion modules
        from data_ingestion.codebase.code_fetcher import CodeFetcher
        from data_ingestion.codebase.code_parser import analyze_codebase
        
        # Use the code fetcher and parser to analyze the codebase
        parsed_files = analyze_codebase()
        
        # Analyze patterns in the code
        pattern_analysis = {
            "total_files": len(parsed_files),
            "total_lines": sum(f.get('lines_of_code', 0) for f in parsed_files),
            "python_files": len([f for f in parsed_files if f['language'] == 'python']),
            "functions_count": sum(len(f['functions']) for f in parsed_files),
            "classes_count": sum(len(f['classes']) for f in parsed_files),
        }
        
        # Extract patterns found from each parsed file
        patterns_found = []
        for file_info in parsed_files:
            if 'potential_issues' in file_info:
                for issue in file_info['potential_issues']:
                    patterns_found.append({
                        "file": file_info['file_path'],
                        "pattern": issue,
                        "language": file_info['language']
                    })
        
        # Process the pattern analysis with Hugging Face model to generate recommendations
        prompt = f"""
        Analyze the following codebase pattern analysis:
        Total files analyzed: {pattern_analysis['total_files']}
        Total lines of code: {pattern_analysis['total_lines']}
        Python files: {pattern_analysis['python_files']}
        Total functions: {pattern_analysis['functions_count']}
        Total classes: {pattern_analysis['classes_count']}
        Patterns found that may indicate optimization opportunities:
        {[p['pattern'] + ' in ' + p['file'] for p in patterns_found[:10]]}  # Show first 10 patterns
        
        Provide specific recommendations for:
        1. Code structure improvements
        2. Performance optimizations
        3. Refactoring opportunities
        4. Best practices to implement
        """
        
        ai_recommendations = _process_with_hf_model(prompt)

        return {
            "analysis": pattern_analysis,
            "patterns_found": patterns_found,
            "recommendations": ai_recommendations
        }