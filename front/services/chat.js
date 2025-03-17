const sidebar_login = document.getElementById('sidebar-login');
const sidebar_histo = document.getElementById('sidebar-histo');
const sidebar_CGU = document.getElementById('sidebar-CGU');
const sidebar_info = document.getElementById('sidebar-info');
const button_box = document.getElementById("buttons-box")
let recoBox = document.getElementById("reco-box");

document.addEventListener('DOMContentLoaded', async function() {
    const token = localStorage.getItem("authToken")

    if (token) {
        const profile_button = document.createElement("button");
        profile_button.classList.add("menu-button");
        profile_button.id = "profile-button";
        profile_button.innerHTML = '<img src="../../assets/power-off.png" alt="History" width="50" draggable="false">';
        profile_button.addEventListener("click", () => {
            disconnect();
        });
        button_box.appendChild(profile_button)

        const histo_button = document.createElement("button");
        histo_button.classList.add("menu-button");
        histo_button.id = "histo-button";
        histo_button.innerHTML = '<img src="../../assets/speech-bubble.png" alt="History" width="50" draggable="false">';
        histo_button.addEventListener("click", () => {
            sidebar_histo.classList.toggle('closed');
        });        
        button_box.appendChild(histo_button)

        fetch('http://localhost:5000/historic', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-KEY': CONFIG.API_KEY,
                'Authorisation': token
            }
        })
        .then(response => {
            if (response.status === 200 || response.status === 201) {
                return response.json()
            } else {
                disconnect();
                return Promise.reject("Échec de la requête");
            }
        })
        .then(response => {
            datas = response.data;
            const params = new URLSearchParams(window.location.search);
            const conversationId = params.get("conversation");

            const chat_box = document.getElementById('chat-box');
    
            if (conversationId) {
                conversation = datas.find(conv => conv.id_conversation == conversationId);
                if (conversation) {
                    let bot = true;
                    for (const message of conversation.messages) {
                        let startingMessage = document.createElement("div");
                        startingMessage.classList.add("message", bot?"bot":"user");
                        startingMessage.textContent = message.content;
                        chat_box.appendChild(startingMessage)
                        bot = !bot
                    }
                    for (const work of conversation.recommendations) {
                        let workRow = document.createElement("div");
                        workRow.classList.add("reco");
                        workRow.textContent = work.title;
                        recoBox.appendChild(workRow);
                    }
                } else {
                    const url = new URL(window.location);
                    url.search = "";
                    window.history.replaceState({}, "", url);
                    window.location.reload();
                }
            }
            else {
                if (datas.length) {
                    const newParams = new URLSearchParams();
                    newParams.set("conversation", datas[datas.length-1].id_conversation);
                    window.location.search = newParams.toString();
                }
                else {
                    newConv(token)
                }
            }
    
            let convRow = document.createElement("div");
            convRow.classList.add("button-conv");
            convRow.textContent = "Nouvelle Conversation";
            convRow.addEventListener("click", () => {
                newConv(token)
            });
            sidebar_histo.appendChild(convRow);
            for (const data of datas) {
                let convRow = document.createElement("div");
                convRow.classList.add("button-conv");
                convRow.textContent = data.name;
                convRow.addEventListener("click", () => {
                    const newParams = new URLSearchParams();
                    newParams.set("conversation", data.id_conversation);
                    window.location.search = newParams.toString();
                });
                sidebar_histo.appendChild(convRow);
            }
        })
        .catch (error => {
            console.error('Erreur:', error);
        })
    }
    else {
        console.log("nkslfnfnpsnpfnoi")
        const button = document.createElement("button");
        button.classList.add("menu-button");
        button.id = "login-button";
        button.innerHTML = '<img src="../../assets/login.png" alt="Connexion" width="50" draggable="false">';
        button.addEventListener("click", () => {
            sidebar_login.classList.toggle('closed');
        });        
        button_box.appendChild(button)
    }
});  

function disconnect() {
    localStorage.clear();
    const url = new URL(window.location);
    url.search = "";
    window.history.replaceState({}, "", url);
    window.location.reload();
}

function newConv(token) {
    fetch('http://localhost:5000/newconv', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-API-KEY': CONFIG.API_KEY,
            'Authorisation': token
        }
    })
    .then(response => {
        if (response.status === 200 || response.status === 201) {
            return response.json()
        } else {
            return Promise.reject("Échec de la requête");
        }
    })
    .then(data => {
        const newParams = new URLSearchParams();
        newParams.set("conversation", data.id);
        window.location.search = newParams.toString();
    });
}

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
        const params = new URLSearchParams(window.location.search);
        const conversationId = params.get("conversation");

        const response = await fetch('http://localhost:5000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-KEY': CONFIG.API_KEY,
            },
            body: JSON.stringify({
                message: input,
                id: conversationId
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


const CGUButton = document.getElementById('CGU-button');
const infoButton = document.getElementById('info-button');

document.addEventListener("click", function(event) {
    const menu = document.getElementById("menu");
    const button = document.querySelector("button");
    const loginButton = document.getElementById('login-button');
    const histoButton = document.getElementById('histo-button');

    if (!menu.contains(event.target) && !button.contains(event.target)) {
        menu.classList.remove("show");
    }

    if (loginButton && !sidebar_login.contains(event.target) && !loginButton.contains(event.target)) {
        sidebar_login.classList.add("closed");
    }

    if (histoButton && !sidebar_histo.contains(event.target) && !histoButton.contains(event.target)) {
        sidebar_histo.classList.add("closed");
    }

    if (CGUButton && !sidebar_CGU.contains(event.target) && !CGUButton.contains(event.target)) {
        sidebar_CGU.classList.add("closed");
    }

    if (infoButton && !sidebar_info.contains(event.target) && !infoButton.contains(event.target)) {
        sidebar_info.classList.add("closed");
    }
});

// Toggle de la classe "closed" au clic sur le bouton
CGUButton.addEventListener('click', function(event) {
    sidebar_CGU.classList.toggle('closed');
});

infoButton.addEventListener('click', function(event) {
    sidebar_info.classList.toggle('closed');
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

