document.getElementById("user-input").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});

async function sendMessage() {
    let userInput = document.getElementById("user-input").value;
    if (userInput.trim() === "") return;
    
    document.getElementById("user-input").value = "";

    let chatBox = document.getElementById("chat-box");

    // Affichage du message de l'utilisateur
    let userMessage = document.createElement("div");
    userMessage.classList.add("message", "user");
    userMessage.textContent = userInput;
    chatBox.appendChild(userMessage);

    // Réponse du chatbot
    let botMessage = document.createElement("div");
    botMessage.classList.add("message", "bot");
    botMessage.textContent = await getBotResponse(userInput);
    chatBox.appendChild(botMessage);

    // Défilement automatique vers le bas
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function getBotResponse(input) {
    try {
        const response = await fetch('http://localhost:5000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',  // Définir le type du contenu
                'X-API-KEY': 'W8Su3FyPlm6PxqEnfb6pcKLP3RnonEHH', // Si tu utilises un token d'authentification
            },
            body: JSON.stringify({
                message: input,
            })
        });
        
        const data = await response.json();  // Convertir la réponse en JSON
        return data.message;  // Retourner le message du bot
    } catch (error) {
        console.error('Erreur:', error);  // Gestion des erreurs
        return "Erreur dans la réponse du bot";  // Message d'erreur par défaut
    }
}
