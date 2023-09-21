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

if(document.getElementById('discord-linking-status') !== null) {
    const s = "{{ isDiscordLinked }}"
    if(s === "true") {
        const linkingStatus = document.getElementById('discord-linking-status')
        linkingStatus.classList.remove("text-red-600")
        linkingStatus.classList.add("text-green-500")
        linkingStatus.innerHTML = "✅ Linked"
        const loginWithDiscord = document.getElementById('login-with-discord')
        loginWithDiscord.classList.remove("flex")
        loginWithDiscord.classList.add("hidden")
        const discordProfile = document.getElementById('discord-profile')
        discordProfile.classList.remove("hidden")
        discordProfile.classList.add("flex")
        const discordProfilePicture = document.getElementById('discord-pfp')
        discordProfilePicture.src = "{{ discordProfilePicture }}"
        const discordUsername = document.getElementById('discord-username')
        discordUsername.innerHTML = "{{ discordUsername }}"
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