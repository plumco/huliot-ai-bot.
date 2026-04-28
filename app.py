<!DOCTYPE html>
<html>
<head>
    <title>Huliot Visual Inspector</title>
    <style>
        /* This is the CSS (Paint) to make it look like a modern app */
        body { background-color: #f4f4f9; font-family: Arial; text-align: center; padding: 50px; }
        .btn { padding: 15px 30px; font-size: 18px; color: white; border: none; border-radius: 5px; cursor: pointer; margin: 10px; }
        .btn-upload { background-color: #28a745; }
        .btn-analyze { background-color: #0056b3; display: none; } /* Hidden until photo is uploaded */
        #imagePreview { max-width: 400px; display: none; border: 2px solid #ccc; border-radius: 10px; margin: 20px auto; }
        
        /* Box for the AI's answer */
        #resultBox { margin: 20px auto; max-width: 600px; background: white; padding: 20px; border-radius: 8px; display: none; box-shadow: 0 4px 8px rgba(0,0,0,0.1); text-align: left; line-height: 1.6;}
        #loading { display: none; color: #0056b3; font-weight: bold; margin-top: 10px; font-size: 18px; }
    </style>
</head>
<body>

    <h1 style="color: #0056b3;">Huliot Pipe Inspector AI</h1>
    <p>Upload a photo of your plumbing issue, and our AI will identify the required Huliot parts.</p>

    <input type="file" id="imageUploader" accept="image/*" style="display: none;">
    
    <!-- Our Two Buttons -->
    <button id="uploadBtn" class="btn btn-upload">1. Upload Photo</button>
    <button id="analyzeBtn" class="btn btn-analyze">2. Analyze with AI</button>

    <img id="imagePreview" src="">

    <!-- Loading Animation -->
    <div id="loading">🧠 AI is analyzing the pipes... please wait...</div>
    
    <!-- Where the answer will appear -->
    <div id="resultBox">
        <h3 style="margin-top:0; color:#0056b3;">Huliot Expert Diagnosis:</h3>
        <div id="aiText"></div>
    </div>

    <!-- ========================================== -->
    <!-- The Electricity (JavaScript)               -->
    <!-- ========================================== -->
    <script>
        // 🚨 IMPORTANT: PASTE YOUR GEMINI API KEY HERE! 🚨
        const myApiKey = "AIzaSyAfsM-pSiBy_1ZVyKR2_ysPV4oyNnkBHIM"; 

        const uploadBtn = document.getElementById("uploadBtn");
        const imageUploader = document.getElementById("imageUploader");
        const imagePreview = document.getElementById("imagePreview");
        const analyzeBtn = document.getElementById("analyzeBtn");
        const loading = document.getElementById("loading");
        const resultBox = document.getElementById("resultBox");
        const aiText = document.getElementById("aiText");

        let base64Image = "";
        let imageMimeType = "";

        // Action 1: Upload Button clicked
        uploadBtn.addEventListener("click", () => imageUploader.click());

        // Action 2: Image is chosen
        imageUploader.addEventListener("change", function(event) {
            const file = event.target.files[0];
            if (file) {
                imageMimeType = file.type;
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    imagePreview.style.display = "block";
                    analyzeBtn.style.display = "inline-block"; // Show the blue AI button!
                    
                    // We turn the image into a secret code (Base64) so the AI can read it
                    base64Image = e.target.result.split(',')[1];
                    resultBox.style.display = "none"; // Hide old results
                }
                reader.readAsDataURL(file);
            }
        });

        // Action 3: Analyze Button clicked!
        analyzeBtn.addEventListener("click", async function() {
            if (!base64Image) return;

            loading.style.display = "block"; // Show "thinking..." text
            resultBox.style.display = "none";
            analyzeBtn.disabled = true;

            // This is the direct phone line to Google Gemini!
            const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${myApiKey}`;
            
            const requestBody = {
                contents: [{
                    parts: [
                        { text: "You are a Huliot Technical Expert. Look closely at this plumbing photo. Identify the pipes or joints shown. If there is a problem or an upgrade needed, explain it briefly. Recommend which specific Huliot product (like Ultra Silent, PP-R, HT, etc.) should be used here. Keep it professional and short." },
                        {
                            inlineData: {
                                mimeType: imageMimeType,
                                data: base64Image
                            }
                        }
                    ]
                }]
            };

            try {
                // Send the image and question to Gemini
                const response = await fetch(url, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(requestBody)
                });
                
                const data = await response.json();
                
                loading.style.display = "none";
                analyzeBtn.disabled = false;

                // Show the AI's answer on the screen!
                if(data.candidates && data.candidates[0].content.parts[0].text) {
                    // This turns computer text into formatted website text
                    let answer = data.candidates[0].content.parts[0].text;
                    answer = answer.replace(/\n/g, '<br>'); // Add line breaks
                    answer = answer.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>'); // Make bold text work
                    
                    aiText.innerHTML = answer;
                    resultBox.style.display = "block";
                }

            } catch (error) {
                loading.style.display = "none";
                analyzeBtn.disabled = false;
                aiText.innerHTML = "Error connecting to AI. Did you remember to paste your API key?";
                resultBox.style.display = "block";
            }
        });
    </script>
</body>
</html>
