if (!DocSenseApi.requireAuth()) throw new Error("Authentication required");

const uploadForm = document.querySelector("#upload-form");
const documentsContainer = document.querySelector("#documents");
const message = document.querySelector("#message");

document.querySelector("#logout-button").addEventListener("click", DocSenseApi.logout);
document.querySelector("#refresh-button").addEventListener("click", loadDocuments);

async function loadDocuments() {
    documentsContainer.textContent = "Загрузка...";
    try {
        const response = await DocSenseApi.request("/documents");
        const documents = await response.json();
        renderDocuments(documents);
    } catch (error) {
        documentsContainer.textContent = error.message;
    }
}

function renderDocuments(documents) {
    documentsContainer.replaceChildren();

    if (!documents.length) {
        const empty = document.createElement("p");
        empty.className = "empty-state";
        empty.textContent = "Документов пока нет. Загрузите первый файл выше.";
        documentsContainer.append(empty);
        return;
    }

    for (const item of documents) {
        const card = document.createElement("article");
        card.className = "document-card";

        const status = document.createElement("span");
        status.className = `status status-${item.status}`;
        status.textContent = item.status;

        const title = document.createElement("h3");
        title.textContent = item.original_filename;

        const meta = document.createElement("p");
        meta.textContent = `${DocSenseApi.formatBytes(item.size)} · ${item.content_type || "неизвестный тип"}`;

        const link = document.createElement("a");
        link.className = "button-link";
        link.href = `/app/documents/${item.id}`;
        link.textContent = "Открыть";

        card.append(status, title, meta, link);
        documentsContainer.append(card);
    }
}

uploadForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const submitButton = uploadForm.querySelector("button");
    const fileInput = uploadForm.elements.file;
    const autoExtract = uploadForm.elements.auto_extract.checked;
    const body = new FormData();
    body.append("file", fileInput.files[0]);

    submitButton.disabled = true;
    DocSenseApi.setMessage(message, "Загружаем документ...");

    try {
        await DocSenseApi.request(`/documents?auto_extract=${autoExtract}`, {
            method: "POST",
            body,
        });
        uploadForm.reset();
        uploadForm.elements.auto_extract.checked = true;
        DocSenseApi.setMessage(message, "Документ загружен.");
        await loadDocuments();
    } catch (error) {
        DocSenseApi.setMessage(message, error.message, true);
    } finally {
        submitButton.disabled = false;
    }
});

loadDocuments();
