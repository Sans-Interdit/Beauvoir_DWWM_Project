const sidebar_login = document.getElementById('sidebar-login');
const sidebar_histo = document.getElementById('sidebar-histo');
const sidebar_CGU = document.getElementById('sidebar-CGU');
const sidebar_info = document.getElementById('sidebar-info');
const sidebar_profile = document.getElementById('sidebar-profile');
const button_box = document.getElementById("buttons-box")
let recoBox = document.getElementById("reco-box");

document.addEventListener('DOMContentLoaded', async function() {
    // Retrieve stored authentication token
    const token = localStorage.getItem("authToken")

    if (token) {
        // Fetch user information using the stored token
        fetch('http://localhost:5000/getuserinfos', {
            method: 'GET',
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
        .then(response => {
            // Update user profile section with fetched data
            document.getElementById("email-profile").textContent = response.email;
            document.getElementById("age-profile").textContent = response.age;
            document.getElementById("country-profile").textContent = response.country;
            document.getElementById("gender-profile").textContent = response.gender;
        })
        .catch(error => {
            console.error('Fetch error:', error);
        });

        // Create profile button dynamically
        const profile_button = document.createElement("button");
        profile_button.classList.add("menu-button");
        profile_button.id = "profile-button";
        profile_button.innerHTML = '<img src="../../assets/user.png" alt="History" width="50" draggable="false">';
        profile_button.addEventListener("click", () => {
            // Toggle profile sidebar visibility
            sidebar_profile.classList.toggle('closed');
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
            // Check if URL has conversation ID
            const params = new URLSearchParams(window.location.search);
            const conversationId = params.get("conversation");

            const chat_box = document.getElementById('chat-box');

            if (conversationId) {
                // Load the specified conversation
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
                    for (const work of conversation.recommendation.oeuvres) {
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
                // If no conversation, start a new one or load the most recent
                if (datas.length) {
                    const newParams = new URLSearchParams();
                    newParams.set("conversation", datas[datas.length-1].id_conversation);
                    window.location.search = newParams.toString();
                }
                else {
                    newConv(token)
                }
            }

            // Add "New Conversation" button in sidebar
            let convRow = document.createElement("div");
            convRow.classList.add("button-conv");
            convRow.textContent = "Nouvelle Conversation";
            convRow.addEventListener("click", () => {
                newConv(token)
            });
            sidebar_histo.appendChild(convRow);
            for (const data of datas) {
                let convRow = document.createElement("div");
                convRow.style.display = "flex";
                convRow.style.alignItems = "center"
                convRow.style.justifyContent = "center"
                convRow.style.width = "100%"

                let conv = document.createElement("div");
                conv.classList.add("button-conv");
                conv.textContent = data.name;
                conv.addEventListener("click", () => {
                    const newParams = new URLSearchParams();
                    newParams.set("conversation", data.id_conversation);
                    window.location.search = newParams.toString();
                });
                convRow.appendChild(conv)


                let supprConv = document.createElement("div");
                supprConv.classList.add("suppr-conv");
                supprConv.innerHTML = '<img src="../../assets/bin.png" alt="History" width="40" draggable="false">';
                supprConv.addEventListener("click", () => {
                    fetch('http://localhost:5000/suppressconv', {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-API-KEY': CONFIG.API_KEY,
                            'Authorisation': token
                        },
                        body: JSON.stringify({
                            id: data.id_conversation
                        }),
                    })
                    .then(response => {
                        if (response.status === 200 || response.status === 201) {
                            return response.json()
                        } else {
                            return Promise.reject("Échec de la requête");
                        }
                    })
                    .then(response => {
                        window.location.reload()
                    })
                    .catch(error => {
                        console.error('Fetch error:', error);
                    });
                });
                convRow.appendChild(supprConv)
                sidebar_histo.appendChild(convRow);
            }
        })
        .catch (error => {
            console.error('Erreur:', error);
        })
    }
    else {
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

    // Clear input field
    document.getElementById("user-input").value = "";

    let chatBox = document.getElementById("chat-box");

    // Display user's message
    let userMessage = document.createElement("div");
    userMessage.classList.add("message", "user");
    userMessage.textContent = userInput;
    chatBox.appendChild(userMessage);

    // Get bot response from backend
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

document.addEventListener("click", function(event) { // Close sidebars when clicking outside
    const menu = document.getElementById("menu");
    const button = document.querySelector("button");
    const loginButton = document.getElementById('login-button');
    const histoButton = document.getElementById('histo-button');
    const profileButton = document.getElementById('profile-button');

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

    if (profileButton && !sidebar_profile.contains(event.target) && !profileButton.contains(event.target)) {
        sidebar_profile.classList.add("closed");
    }
});

CGUButton.addEventListener('click', function(event) {
    sidebar_CGU.classList.toggle('closed');
});

infoButton.addEventListener('click', function(event) {
    sidebar_info.classList.toggle('closed');
});

document.getElementById("toggle-form").addEventListener("click", function() {
    // Switch between login and registration form states
    const title = document.getElementById("form-title");
    const form = document.getElementById("auth-form");
    const authDiv = document.getElementById("auth-div");
    const button = form.querySelector("button");

    if (title.textContent === "Connexion") {
        title.textContent = "Inscription";
        authDiv.style.alignItems = "center";
        authDiv.style.display = "flex";
        button.textContent = "S'inscrire";
        this.textContent = "Déjà inscrit ? Se connecter";

        document.getElementById("confirm-password").setAttribute("required", "");
        document.getElementById("age-input").setAttribute("required", "");
        document.getElementById("country-input").setAttribute("required", "");
        document.getElementById("gender-male").setAttribute("required", "");
        document.getElementById("terms").setAttribute("required", "");
        document.getElementById("terms").addEventListener("change", function () {
            if (!this.checked) {
                this.setCustomValidity("Vous devez accepter les CGU.");
            } else {
                this.setCustomValidity("");
            }
        });
    } else {
        title.textContent = "Connexion";
        authDiv.style.display = "none";
        button.textContent = "Se connecter";
        this.textContent = "Pas encore inscrit ? S'inscrire";

        document.getElementById("confirm-password").removeAttribute("required");
        document.getElementById("age-input").removeAttribute("required");
        document.getElementById("country-input").removeAttribute("required");
        document.getElementById("gender-male").removeAttribute("required");
        document.getElementById("terms").removeAttribute("required");
    }
});

document.getElementById("auth-form").addEventListener("submit", function(event) {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirm-password").value;
    const age = document.getElementById("age-input").value;
    const country = document.getElementById("country-input").value;
    const isRegistering = document.getElementById("form-title").textContent === "Inscription";
    const radios = document.querySelectorAll('input[name="gender"]');
    const checkbox = document.getElementById("checkbox");

    function getSelectedGender() {
        for (const radio of radios) {
            if (radio.checked) {
            return radio.value;
            }
        }
        return null;
    }

    const gender = getSelectedGender();

    if (isRegistering && password !== confirmPassword) {
        alert("Les mots de passe ne correspondent pas !");
        return;
    }

    const formData = {email, password, age, country, gender};

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
        if (response.token) {
            localStorage.setItem("authToken", response.token);
        }
        window.location.href = "chat.html";
    })
    .catch(error => {
        console.error("Erreur :", error);
        alert(isRegistering ? `Échec de l'inscription` : `Échec de la connexion`);
    });
});

function supprAcc() {
    fetch('http://localhost:5000/suppressacc', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-API-KEY': CONFIG.API_KEY,
            'Authorisation': localStorage.getItem("authToken")
        }
    })
    .then(response => {
        if (response.status === 200 || response.status === 201) {
            return response.json()
        } else {
            return Promise.reject("Échec de la requête");
        }
    })
    .then(response => {
        disconnect();
    })
    .catch(error => {
        console.error('Fetch error:', error);
    });
}

const countries = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua & Deps",
    "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan", "Bahamas",
    "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin",
    "Bhutan", "Bolivia", "Bosnia Herzegovina", "Botswana", "Brazil", "Brunei",
    "Bulgaria", "Burkina", "Burundi", "Cambodia", "Cameroon", "Canada",
    "Cape Verde", "Central African Rep", "Chad", "Chile", "China", "Colombia",
    "Comoros", "Congo", "Congo {Democratic Rep}", "Costa Rica", "Croatia", "Cuba",
    "Cyprus", "Czech Republic", "Denmark", "Djibouti", "Dominica", "Dominican Republic",
    "East Timor", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea",
    "Estonia", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Gambia", "Georgia",
    "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau",
    "Guyana", "Haiti", "Honduras", "Hungary", "Iceland", "India", "Indonesia", "Iran",
    "Iraq", "Ireland {Republic}", "Israel", "Italy", "Ivory Coast", "Jamaica", "Japan",
    "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea North", "Korea South", "Kosovo",
    "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya",
    "Liechtenstein", "Lithuania", "Luxembourg", "Macedonia", "Madagascar", "Malawi",
    "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania",
    "Mauritius", "Mexico", "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro",
    "Morocco", "Mozambique", "Myanmar, {Burma}", "Namibia", "Nauru", "Nepal",
    "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "Norway", "Oman",
    "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru",
    "Philippines", "Poland", "Portugal", "Qatar", "Romania", "Russian Federation",
    "Rwanda", "St Kitts & Nevis", "St Lucia", "Saint Vincent & the Grenadines",
    "Samoa", "San Marino", "Sao Tome & Principe", "Saudi Arabia", "Senegal", "Serbia",
    "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands",
    "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "Sudan",
    "Suriname", "Swaziland", "Sweden", "Switzerland", "Syria", "Taiwan", "Tajikistan",
    "Tanzania", "Thailand", "Togo", "Tonga", "Trinidad & Tobago", "Tunisia", "Turkey",
    "Turkmenistan", "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates",
    "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu",
    "Vatican City", "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe"
  ];

const datalistCountries = document.getElementById("countries");
countries.forEach(country => {
    let option = document.createElement("option");
    option.value = country;
    datalistCountries.appendChild(option);
});

genres = ["Supernatural", "Suspense", "Slice of Life", 'Gourmet', 'Avant Garde', 'Action', 'Science Fiction', 'Adventure',
        'Drama', 'Crime', 'Thriller', 'Fantasy', 'Comedy', 'Romance', 'Western', 'Mystery', 'War', 'Animation',
        'Family', 'Horror', 'Music', 'History', 'TV Movie', 'Documentary']

const datalistGenres = document.getElementById("genres");
genres.forEach(genre => {
    let option = document.createElement("option");
    option.value = genre;
    datalistGenres.appendChild(option);
});

const genreInput = document.getElementById("genres-input");
const listGenres = document.getElementById("genres-list");
function addGenre() {
    fetch('http://localhost:5000/addgenre', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-API-KEY': CONFIG.API_KEY,
            'Authorisation': localStorage.getItem("authToken")
        },
        body: JSON.stringify({
            name : genreInput.value
        })
    })
    .then(response => {
        if (response.status === 200 || response.status === 201) {
            return response.json()
        } else {
            return Promise.reject("Échec de la requête");
        }
    })
    .then(response => {
        id = response.id
        console.log(id)
        const threeGenresDivs = document.getElementsByClassName("three-genres-div")
        let threeGenresDiv;
        if (threeGenresDivs.length > 0) {
            console.log(threeGenresDivs[threeGenresDivs.length - 1].children.length)
            if (threeGenresDivs[threeGenresDivs.length - 1].children.length > 2) {
                threeGenresDiv = document.createElement("div")
                threeGenresDiv.classList.add("three-genres-div")
            }
            else {
                console.log(threeGenresDivs)
                threeGenresDiv = threeGenresDivs[threeGenresDivs.length - 1]
            }
        }
        else {
            threeGenresDiv = document.createElement("div")
            threeGenresDiv.classList.add("three-genres-div")
        }
        let genreDiv = document.createElement("div")
        genreDiv.classList.add("genre-div")
        let titleGenre = document.createElement("h3")
        titleGenre.textContent = genreInput.value
        let supprGenreButton = document.createElement("button")
        supprGenreButton.classList.add("suppr-conv")
        supprGenreButton.innerHTML = "<img src='../../assets/bin.png' alt='Supprimer' width='20' draggable='false'>"
        supprGenreButton.addEventListener("click", () => {
            fetch('http://localhost:5000/suppressgenre', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-KEY': CONFIG.API_KEY,
                    'Authorisation': localStorage.getItem("authToken")
                },
                body: JSON.stringify({
                    id: id
                })
            })
            .then(response => {
                if (response.status === 200 || response.status === 201) {
                    return response.json()
                } else {
                    return Promise.reject("Échec de la requête");
                }
            })
            .then(response => {
                genreDiv.remove();
            })
            .catch(error => {
                console.error('Fetch error:', error);
            });
        });
        genreDiv.appendChild(titleGenre);
        genreDiv.appendChild(supprGenreButton);
        threeGenresDiv.appendChild(genreDiv);
        listGenres.appendChild(threeGenresDiv);
    })
    .catch(error => {
        console.error('Fetch error:', error);
    });
}
