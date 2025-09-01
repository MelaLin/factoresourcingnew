from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/test", response_class=HTMLResponse)
async def test_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Backend Test Page</title>
    </head>
    <body>
        <h1>Backend API Test</h1>
        <p>If you can see this page, the backend is working!</p>
        
        <h2>Test API Endpoints:</h2>
        <button onclick="testAPI()">Test Search API</button>
        <div id="result"></div>
        
        <script>
        async function testAPI() {
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = 'Testing...';
            
            try {
                const response = await fetch('/api/search/keyword', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ keyword: 'hvac' }),
                });
                
                const data = await response.json();
                resultDiv.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            } catch (error) {
                resultDiv.innerHTML = 'Error: ' + error.message;
            }
        }
        </script>
    </body>
    </html>
    """
