document.addEventListener('DOMContentLoaded', async function() {
    try {
        console.log(localStorage.getItem("authToken"))
        const response = await fetch('http://localhost:5000/historic', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-KEY': CONFIG.API_KEY,
                'Authorisation': localStorage.getItem("authToken")
            }
        });
        console.log(response)
    } catch (error) {
        console.error('Erreur:', error);
        return 400;
    }
});  

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

const sidebar_login = document.getElementById('sidebar-login');
const loginButton = document.getElementById('login-button');

// Fermer le menu si on clique en dehors
document.addEventListener("click", function(event) {
    const menu = document.getElementById("menu");
    const button = document.querySelector("button");

    if (!menu.contains(event.target) && !button.contains(event.target)) {
        menu.classList.remove("show");
    }

    if (!sidebar_login.contains(event.target) && !loginButton.contains(event.target)) {
        sidebar_login.classList.add("closed");
    }
});

// Toggle de la classe "closed" au clic sur le bouton
loginButton.addEventListener('click', function(event) {
    sidebar_login.classList.toggle('closed');
    event.stopPropagation();
});

document.getElementById("toggle-form").addEventListener("click", function() {
    const title = document.getElementById("form-title");
    const form = document.getElementById("auth-form");
    const confirmPassword = document.getElementById("confirm-password");
    const button = form.querySelector("button");

    if (title.textContent === "Connexion") {
        title.textContent = "Inscription";
        confirmPassword.style.display = "block";
        button.textContent = "S'inscrire";
        this.textContent = "Déjà inscrit ? Se connecter";
    } else {
        title.textContent = "Connexion";
        confirmPassword.style.display = "none";
        button.textContent = "Se connecter";
        this.textContent = "Pas encore inscrit ? S'inscrire";
    }
});

document.getElementById("auth-form").addEventListener("submit", function(event) {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirm-password").value;
    const isRegistering = document.getElementById("form-title").textContent === "Inscription";

    if (isRegistering && password !== confirmPassword) {
        alert("Les mots de passe ne correspondent pas !");
        return;
    }

    const formData = { email, password };

    fetch(`http://localhost:5000/${isRegistering ? "register": "login"}`, {
        method: "POST",
        headers: { 
            "Content-Type": "application/json" ,
            'X-API-KEY': CONFIG.API_KEY,
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        if (response.status === 200 || response.status === 201) {
            return response.json()
        } else {
            return Promise.reject("Échec de la requête");
        }
    })
    .then(response => {
        // Sauvegarder le token dans le localStorage
        if (response.token) {
            console.log(response.token)
            localStorage.setItem("authToken", response.token);
        }
        window.location.href = "chat.html";
    })
    .catch(error => {
        console.error("Erreur :", error);
        alert(isRegistering ? `Échec de l'inscription` : `Échec de la connexion`);
    });
});
