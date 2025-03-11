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
            alert(isRegistering ? `Échec de l'inscription : ${response}` : `Échec de la connexion : ${response}`);
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
        alert("Une erreur s'est produite.");
    });
});
