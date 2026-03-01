/*
 * Test script to verify frontend can connect to backend API
 * Run with: node test_connection.js
 */

const axios = require('axios');

// Test the connection to the backend API
async function testConnection() {
  try {
    console.log('Testing connection to NudgeAI Simple API Server...');
    
    // Test health endpoint
    console.log('1. Testing health endpoint...');
    const healthResponse = await axios.get('http://localhost:8001/health');
    console.log('✓ Health check passed:', healthResponse.data);
    
    // Test calendar endpoint
    console.log('2. Testing calendar endpoint...');
    const calendarResponse = await axios.get('http://localhost:8001/api/mcp/tools/query_calendar');
    console.log('✓ Calendar endpoint passed, received', calendarResponse.data.result.events.length, 'events');
    
    // Test drive endpoint
    console.log('3. Testing drive endpoint...');
    const driveResponse = await axios.get('http://localhost:8001/api/mcp/tools/query_drive');
    console.log('✓ Drive endpoint passed, received', driveResponse.data.result.documents.length, 'documents');
    
    // Test location endpoint
    console.log('4. Testing location endpoint...');
    const locationResponse = await axios.get('http://localhost:8001/api/mcp/tools/query_location');
    console.log('✓ Location endpoint passed, received', locationResponse.data.result.locations.length, 'locations');
    
    // Test health/fitness endpoint
    console.log('5. Testing health endpoint...');
    const healthDataResponse = await axios.get('http://localhost:8001/api/mcp/tools/query_fit');
    console.log('✓ Health endpoint passed');
    
    console.log('\n🎉 All API endpoints are working correctly!');
    console.log('The frontend should be able to connect to the backend successfully.');
    console.log('\nTo start the frontend:');
    console.log('1. cd frontend');
    console.log('2. npm install (if first time)');
    console.log('3. npm run dev');
    console.log('\nThe Vite proxy will forward /api requests to http://localhost:8001');
    
  } catch (error) {
    console.error('❌ Error connecting to API server:', error.message);
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
    }
  }
}

testConnection();