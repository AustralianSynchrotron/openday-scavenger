function updateAnswer(e)
{
    const answerInputBox = document.getElementById("answer");
    answerInputBox.value=e.target.value;
}


document.addEventListener('DOMContentLoaded', () => {
    const radios = document.querySelectorAll(".form-option");
    radios.forEach(option => {
        const radioBtn = document.getElementById(option.getAttribute("id"));
        radioBtn.addEventListener('click', updateAnswer);
    });
});
 