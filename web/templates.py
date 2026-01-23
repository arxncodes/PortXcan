def index_page():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>PortXcan | Network Scanner</title>
    <style>
        body {
            margin: 0;
            font-family: "Segoe UI", Arial, sans-serif;
            background: radial-gradient(circle at top, #0f172a, #020617);
            color: #e5e7eb;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .container {
            background: rgba(2, 6, 23, 0.9);
            border: 1px solid #1e293b;
            border-radius: 14px;
            padding: 40px;
            width: 420px;
            box-shadow: 0 0 40px rgba(56, 189, 248, 0.15);
            animation: fadeIn 0.8s ease;
        }

        h1 {
            text-align: center;
            color: #38bdf8;
        }

        input, button {
            width: 100%;
            padding: 12px;
            margin-top: 15px;
            background: #020617;
            border: 1px solid #1e293b;
            border-radius: 8px;
            color: #e5e7eb;
        }

        button {
            background: linear-gradient(135deg, #2563eb, #38bdf8);
            color: #020617;
            font-weight: bold;
            cursor: pointer;
        }

        button:hover {
            box-shadow: 0 0 20px rgba(56, 189, 248, 0.5);
        }

        .loader {
            display: none;
            margin-top: 20px;
            text-align: center;
        }

        .spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #1e293b;
            border-top: 4px solid #38bdf8;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: auto;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>

    <script>
        function startScan() {
            document.getElementById("loader").style.display = "block";
        }
    </script>
</head>

<body>
<div class="container">
    <h1>PortXcan</h1>

    <form method="post" action="/scan" onsubmit="startScan()">
        <input name="target" placeholder="IP / Host / CIDR" required>
        <input name="start" value="1">
        <input name="end" value="1024">
        <button type="submit">Start Scan</button>
    </form>

    <div class="loader" id="loader">
        <div class="spinner"></div>
        <p>Scanning network...</p>
    </div>
</div>
</body>
</html>
"""
