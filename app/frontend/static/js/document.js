if (!DocSenseApi.requireAuth()) throw new Error("Authentication required");

const documentId = Number(window.location.pathname.split("/").pop());
const message = document.querySelector("#message");
const documentName = document.querySelector("#document-name");
const documentMeta = document.querySelector("#document-meta");
const documentStatus = document.querySelector("#document-status");
const textOutput = document.querySelector("#document-text");
const processButton = document.querySelector("#process-button");
const versionsContainer = document.querySelector("#versions");
const versionFrom = document.querySelector("#version-from");
const versionTo = document.querySelector("#version-to");
const diffResult = document.querySelector("#diff-result");
let currentDocument;

document.querySelector("#logout-button").addEventListener("click", DocSenseApi.logout);
processButton.addEventListener("click", processDocument);
document.querySelector("#text-button").addEventListener("click", loadText);
document.querySelector("#download-button").addEventListener("click", downloadDocument);
document.querySelector("#delete-button").addEventListener("click", deleteDocument);
document.querySelector("#version-form").addEventListener("submit", uploadVersion);
document.querySelector("#diff-form").addEventListener("submit", compareVersions);

async function loadDocument() {
    try {
        const response = await DocSenseApi.request(`/documents/${documentId}`);
        currentDocument = await response.json();
        documentName.textContent = currentDocument.original_filename;
        documentMeta.textContent = `${DocSenseApi.formatBytes(currentDocument.size)} · ${currentDocument.content_type || "неизвестный тип"}`;
        documentStatus.textContent = currentDocument.status;
        documentStatus.className = `status status-${currentDocument.status}`;
        processButton.hidden = currentDocument.status === "ready";

        if (currentDocument.status === "ready") {
            await loadText();
        }

        if (currentDocument.error) {
            DocSenseApi.setMessage(message, currentDocument.error, true);
        }
    } catch (error) {
        DocSenseApi.setMessage(message, error.message, true);
    }
}

async function processDocument() {
    DocSenseApi.setMessage(message, "Извлекаем текст...");
    try {
        await DocSenseApi.request(`/documents/${documentId}/process`, {method: "POST"});
        DocSenseApi.setMessage(message, "Текст извлечён.");
        await loadDocument();
    } catch (error) {
        DocSenseApi.setMessage(message, error.message, true);
    }
}

async function loadText() {
    textOutput.textContent = "Загрузка текста...";
    try {
        const response = await DocSenseApi.request(`/documents/${documentId}/text`);
        textOutput.textContent = await response.text();
    } catch (error) {
        textOutput.textContent = error.message;
    }
}

async function downloadDocument() {
    try {
        const response = await DocSenseApi.request(`/documents/${documentId}/file`);
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = currentDocument.original_filename;
        link.click();
        URL.revokeObjectURL(url);
    } catch (error) {
        DocSenseApi.setMessage(message, error.message, true);
    }
}

async function deleteDocument() {
    if (!window.confirm("Удалить документ и все его версии?")) return;
    try {
        await DocSenseApi.request(`/documents/${documentId}`, {method: "DELETE"});
        window.location.href = "/app/documents";
    } catch (error) {
        DocSenseApi.setMessage(message, error.message, true);
    }
}

async function loadVersions() {
    versionsContainer.textContent = "Загрузка версий...";
    try {
        const response = await DocSenseApi.request(`/documents/${documentId}/versions`);
        const versions = await response.json();
        renderVersions(versions);
    } catch (error) {
        versionsContainer.textContent = error.message;
    }
}

function renderVersions(versions) {
    versionsContainer.replaceChildren();
    versionFrom.replaceChildren();
    versionTo.replaceChildren();

    if (!versions.length) {
        versionsContainer.textContent = "Дополнительных версий пока нет.";
        return;
    }

    for (const version of versions) {
        const row = document.createElement("div");
        row.className = "version-row";

        const info = document.createElement("span");
        info.textContent = `Версия ${version.version_number}${version.similarity == null ? "" : ` · сходство ${(version.similarity * 100).toFixed(0)}%`}`;

        const button = document.createElement("button");
        button.className = "button-secondary";
        button.type = "button";
        button.textContent = "Показать текст";
        button.addEventListener("click", () => showVersion(version.version_number));
        row.append(info, button);
        versionsContainer.append(row);

        for (const select of [versionFrom, versionTo]) {
            const option = document.createElement("option");
            option.value = version.version_number;
            option.textContent = `Версия ${version.version_number}`;
            select.append(option);
        }
    }

    if (versions.length > 1) versionTo.selectedIndex = versions.length - 1;
}

async function showVersion(versionNumber) {
    textOutput.textContent = `Загрузка версии ${versionNumber}...`;
    try {
        const response = await DocSenseApi.request(`/documents/${documentId}/versions/${versionNumber}`);
        const version = await response.json();
        textOutput.textContent = version.extracted_text;
        textOutput.scrollIntoView({behavior: "smooth"});
    } catch (error) {
        textOutput.textContent = error.message;
    }
}

async function uploadVersion(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const submitButton = form.querySelector("button");
    const body = new FormData();
    body.append("file", form.elements.file.files[0]);
    submitButton.disabled = true;
    DocSenseApi.setMessage(message, "Загружаем новую версию...");

    try {
        const response = await DocSenseApi.request(`/documents/${documentId}/versions`, {
            method: "POST",
            body,
        });
        const version = await response.json();
        form.reset();
        DocSenseApi.setMessage(message, version.msg || `Версия ${version.version_number} создана.`);
        await loadVersions();
    } catch (error) {
        DocSenseApi.setMessage(message, error.message, true);
    } finally {
        submitButton.disabled = false;
    }
}

async function compareVersions(event) {
    event.preventDefault();
    if (versionFrom.value === versionTo.value) {
        diffResult.textContent = "Выберите разные версии.";
        return;
    }

    diffResult.textContent = "AI анализирует изменения...";
    try {
        const response = await DocSenseApi.request(`/documents/${documentId}/diff`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                version_from: Number(versionFrom.value),
                version_to: Number(versionTo.value),
            }),
        });
        const result = await response.json();
        diffResult.textContent = result.diff_summary;
    } catch (error) {
        diffResult.textContent = error.message;
    }
}

Promise.all([loadDocument(), loadVersions()]);
