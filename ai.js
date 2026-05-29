// ==========================================
// HULIOT SMART WHATSAPP ASSISTANT MASTER CODE
// ==========================================

const express = require('express');
const { GoogleGenerativeAI } = require('@google/generative-ai');

const app = express();
app.use(express.json());

// --- 1. YOUR SECRET KEYS & URLs ---
const GEMINI_API_KEY = "PASTE_GEMINI_KEY_HEREAIzaSyAfsM-pSiBy_1ZVyKR2_ysPV4oyNnkBHIM";
const GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1a8cAUPwcNv7NFz1SjdKWwWpIqsKM9hALRGDEEqEF-5Y/edit?gid=0#gid=0";

// You will get these from your Meta Developer Dashboard
const WHATSAPP_TOKEN = "PASTE_META_TEMPORARY_ACCESS_TOKEN_HERE"; 
const WHATSAPP_PHONE_ID = "PASTE_META_PHONE_NUMBER_ID_HERE"; 
const WEBHOOK_VERIFY_TOKEN = "huliot123"; // This is a password we make up for Meta

const genAI = new GoogleGenerativeAI(GEMINI_API_KEY);

// --- 2. THE SYSTEM PROMPT (Training the AI for your business) ---
const HULIOT_SYSTEM_PROMPT = `
You are the expert Technical Manager for Huliot India. 
Your job is to answer questions from plumbers, contractors, and architects about Huliot products (like Ultra Silent acoustic pipes, drainage systems, etc.).
Keep your answers professional, technical but easy to understand, and no longer than 3-4 sentences. 
If they greet you, politely introduce yourself as the Huliot Technical AI Assistant.
`;

// --- 3. VERIFYING THE RECEPTIONIST (Meta Webhook Setup) ---
// Meta will check this link once to make sure our server is real.
app.get('/webhook', (req, res) => {
    const mode = req.query['hub.mode'];
    const token = req.query['hub.verify_token'];
    const challenge = req.query['hub.challenge'];

    if (mode === 'subscribe' && token === WEBHOOK_VERIFY_TOKEN) {
        console.log("✅ Meta Webhook Verified!");
        res.status(200).send(challenge);
    } else {
        res.sendStatus(403);
    }
});

// --- 4. RECEIVING & ANSWERING MESSAGES ---
app.post('/webhook', async (req, res) => {
    // Tell Meta we received the message immediately so they don't resend it
    res.sendStatus(200); 

    try {
        const body = req.body;
        
        // Check if this is a real WhatsApp message
        if (body.object && body.entry && body.entry[0].changes[0].value.messages) {
            const messageData = body.entry[0].changes[0].value.messages[0];
            const senderPhone = messageData.from;
            const userQuestion = messageData.text.body;

            console.log(`📩 New message from ${senderPhone}: ${userQuestion}`);

            // Step A: Ask Gemini for the answer
            const model = genAI.getGenerativeModel({ 
                model: "gemini-2.5-flash",
                systemInstruction: HULIOT_SYSTEM_PROMPT
            });
            const result = await model.generateContent(userQuestion);
            const aiAnswer = result.response.text();

            // Step B: Send the answer back to the user on WhatsApp
            await fetch(`https://graph.facebook.com/v18.0/${WHATSAPP_PHONE_ID}/messages`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${WHATSAPP_TOKEN}`,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    messaging_product: "whatsapp",
                    to: senderPhone,
                    type: "text",
                    text: { body: aiAnswer }
                })
            });
            console.log(`📤 Reply sent to ${senderPhone}`);

            // Step C: Save everything to your Google Sheets Logbook
            await fetch(GOOGLE_SHEET_URL, {
                method: "POST",
                body: JSON.stringify({
                    phone: senderPhone,
                    question: userQuestion,
                    answer: aiAnswer
                })
            });
            console.log("📝 Saved to Google Sheets");
        }
    } catch (error) {
        console.error("❌ Error processing message:", error);
    }
});

// --- 5. START THE SERVER ---
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`🚀 Huliot Server is running on port ${PORT}`);
});
=