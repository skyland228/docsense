const DocSenseApi = (() => {
    const tokenKey = "docsense_access_token";
    const usernameKey = "docsense_username";

    function getToken() {
        return localStorage.getItem(tokenKey);
    }

    function saveSession(token, username) {
        localStorage.setItem(tokenKey, token);
        localStorage.setItem(usernameKey, username);
    }

    function clearSession() {
        localStorage.removeItem(tokenKey);
        localStorage.removeItem(usernameKey);
    }

    function requireAuth() {
        if (!getToken()) {
            window.location.href = "/";
            return false;
        }
        return true;
    }

    function logout() {
        clearSession();
        window.location.href = "/";
    }

    async function request(path, options = {}) {
        const headers = new Headers(options.headers || {});
        const token = getToken();

        if (token) {
            headers.set("Authorization", `Bearer ${token}`);
        }

        const response = await fetch(path, {...options, headers});

        if (response.status === 401 && token) {
            clearSession();
            window.location.href = "/";
            throw new Error("Сессия закончилась. Войдите снова.");
        }

        if (!response.ok) {
            let detail = `Ошибка ${response.status}`;
            try {
                const body = await response.json();
                detail = typeof body.detail === "string" ? body.detail : detail;
            } catch (_) {
                const text = await response.text();
                if (text) detail = text;
            }
            throw new Error(detail);
        }

        return response;
    }

    function formatBytes(bytes) {
        if (bytes < 1024) return `${bytes} Б`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} КБ`;
        return `${(bytes / 1024 / 1024).toFixed(1)} МБ`;
    }

    function setMessage(element, text, isError = false) {
        element.textContent = text;
        element.classList.toggle("message-error", isError);
    }

    return {
        clearSession,
        formatBytes,
        getToken,
        logout,
        request,
        requireAuth,
        saveSession,
        setMessage,
    };
})();
