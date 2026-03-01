const { exec } = require('child_process');

// Function to execute git commit with increased buffer size
function executeGitCommit(message) {
    return new Promise((resolve, reject) => {
        // Increase buffer to 10MB (1024 * 1024 * 10)
        exec(`git commit -m "${message}"`, { maxBuffer: 1024 * 1024 * 10 }, (error, stdout, stderr) => {
            if (error) {
                console.error('Error executing git commit:', error);
                reject(error);
                return;
            }
            
            console.log('Git commit successful!');
            console.log('Output:', stdout);
            if (stderr) {
                console.log('Stderr:', stderr);
            }
            
            resolve({ stdout, stderr });
        });
    });
}

// Example usage
async function commitChanges() {
    try {
        const message = "Nudgeai";
        const result = await executeGitCommit(message);
        console.log('Commit completed successfully');
    } catch (error) {
        console.error('Commit failed:', error);
    }
}

// Export the function for use in other modules
module.exports = { executeGitCommit, commitChanges };

// If this file is run directly, execute the commit
if (require.main === module) {
    commitChanges();
}
