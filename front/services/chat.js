// document.addEventListener('DOMContentLoaded', async function() {
//     try {
//         const response = await fetch('http://localhost:5000/results', {
//             method: 'GET',
//             headers: {
//                 'Content-Type': 'application/json',
//             }
//         });
//         let chatBox = document.getElementById("reco-box");

//         const data = await response.json(); 
//         for (const work of data) {
//             let userMessage = document.createElement("div");
//             userMessage.classList.add("reco");
//             userMessage.textContent = work.title;
//             chatBox.appendChild(userMessage);
//         }
//     } catch (error) {
//         console.error('Erreur:', error);
//         return 400;
//     }
// });  

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
    let recoBox = document.getElementById("reco-box");

    // Affichage du message de l'utilisateur
    let userMessage = document.createElement("div");
    userMessage.classList.add("message", "user");
    userMessage.textContent = userInput;
    chatBox.appendChild(userMessage);

    // Réponse du chatbot
    let botMessage = document.createElement("div");
    botMessage.classList.add("message", "bot");
    response = await getBotResponse(userInput);
    botMessage.textContent = response.message;
    works = response.works;
    if (works) {
        recoBox.innerHTML = "";
        for (const work of works) {
            let workRow = document.createElement("div");
            workRow.classList.add("reco");
            workRow.textContent = work.title;
            recoBox.appendChild(workRow);
        }
    }
    chatBox.appendChild(botMessage);

    // Défilement automatique vers le bas
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function getBotResponse(input) {
    try {
        const response = await fetch('http://localhost:5000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-KEY': CONFIG.API_KEY,
            },
            body: JSON.stringify({
                message: input,
            }),
            mode: "cors"
        });
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Erreur:', error);
        return "Erreur dans la réponse du bot";
    }
}


function toggleMenu() {
    document.getElementById("menu").classList.toggle("show");
}

// Fermer le menu si on clique en dehors
document.addEventListener("click", function(event) {
    const menu = document.getElementById("menu");
    const button = document.querySelector("button");

    if (!menu.contains(event.target) && !button.contains(event.target)) {
        menu.classList.remove("show");
    }
});