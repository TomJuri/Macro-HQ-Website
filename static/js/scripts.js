if (document.getElementById('signin-form') !== null) {
    document.getElementById('signin-form').addEventListener('submit', function (event) {
        event.preventDefault();
        signInOrUp(new FormData(this))
    });
}

if (document.getElementById('signup-form') !== null) {
    document.getElementById('signup-form').addEventListener('submit', function (event) {
        event.preventDefault();
        signInOrUp(new FormData(this))
    });
}

if(document.getElementById("isDiscordLinked") !== null) {
    if(document.getElementById("isDiscordLinked").innerHTML === "true") {
        const loginWithDiscord = document.getElementById('login-with-discord')
        loginWithDiscord.classList.remove("flex")
        loginWithDiscord.classList.add("hidden")
        const discordProfile = document.getElementById('discord-profile')
        discordProfile.classList.remove("hidden")
        discordProfile.classList.add("flex")
        const signOutOfDiscord = document.getElementById('signout-of-discord')
        signOutOfDiscord.classList.remove("hidden")
        signOutOfDiscord.classList.add("flex")
    }
}

function signInOrUp(formData) {
    const fetchOptions = {
        method: 'POST', body: formData
    };
    fetch("#", fetchOptions)
        .then(response => {
            if (!response.ok) {
                return response.json();
            } else {
                const queryString = window.location.search;
                const urlParams = new URLSearchParams(queryString);
                const nextValue = urlParams.get('next');
                if (nextValue) {
                    window.location.href = `/${nextValue}`;
                } else {
                    window.location.href = '/';
                }
            }
        })
        .then(data => {
            document.getElementById('error-message').classList.remove('hidden');
            document.getElementById('error-message').innerHTML = data["error"];
        })
}