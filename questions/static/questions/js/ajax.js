function getCookie(name) {
    const cookies = document.cookie ? document.cookie.split(";") : [];

    for (let cookie of cookies) {
        cookie = cookie.trim();

        if (cookie.startsWith(name + "=")) {
            return decodeURIComponent(cookie.substring(name.length + 1));
        }
    }

    return null;
}

function showAjaxError(message) {
    alert(message || "Произошла ошибка. Попробуйте ещё раз.");
}

async function sendAjaxPost(url, data) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "X-Requested-With": "XMLHttpRequest",
        },
        body: data,
    });

    let payload = null;

    try {
        payload = await response.json();
    } catch (error) {
        throw new Error("Сервер вернул некорректный ответ.");
    }

    if (!response.ok || !payload.ok) {
        throw new Error(payload.error || "Ошибка запроса.");
    }

    return payload;
}

function setupVoting() {
    document.querySelectorAll("[data-vote-button]").forEach((button) => {
        button.addEventListener("click", async () => {
            if (button.disabled) {
                return;
            }

            const voteBox = button.closest("[data-vote-box]");
            const ratingElement = voteBox.querySelector("[data-rating]");
            const url = button.dataset.url;
            const value = button.dataset.value;
            const entityType = button.dataset.entityType;
            const entityId = button.dataset.entityId;

            const data = new FormData();
            data.append("value", value);

            if (entityType === "question") {
                data.append("question_id", entityId);
            }

            if (entityType === "answer") {
                data.append("answer_id", entityId);
            }

            try {
                const payload = await sendAjaxPost(url, data);
                ratingElement.textContent = payload.rating;

                voteBox.querySelectorAll("[data-vote-button]").forEach((item) => {
                item.classList.remove("vote-btn-active");
            });

            if (payload.user_vote !== null) {
                button.classList.add("vote-btn-active");
}
            } catch (error) {
                showAjaxError(error.message);
            }
        });
    });
}

function setupCorrectAnswer() {
    document.querySelectorAll("[data-correct-answer]").forEach((checkbox) => {
        checkbox.addEventListener("change", async () => {
            if (checkbox.disabled) {
                return;
            }

            const data = new FormData();
            data.append("question_id", checkbox.dataset.questionId);
            data.append("answer_id", checkbox.dataset.answerId);

            try {
                const payload = await sendAjaxPost(checkbox.dataset.url, data);

                document.querySelectorAll("[data-correct-answer]").forEach((item) => {
                    item.checked = false;
                });

                const selected = document.querySelector(
                    `[data-correct-answer][data-answer-id="${payload.correct_answer_id}"]`
                );

                if (selected) {
                    selected.checked = true;
                }
            } catch (error) {
                checkbox.checked = !checkbox.checked;
                showAjaxError(error.message);
            }
        });
    });
}

document.addEventListener("DOMContentLoaded", () => {
    setupVoting();
    setupCorrectAnswer();
});