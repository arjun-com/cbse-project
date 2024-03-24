var test_taker_page_idx = 0
var test_taker_prev_page_btn = document.getElementById("test-taker-prev-page-btn")
var test_taker_option_btns = document.getElementsByClassName("test-taker-option-btn")
var pages = document.getElementsByClassName("test-taker-page")

var selected_options = {}

for(const btn of test_taker_option_btns) {
    btn.addEventListener("click", function() {

    })
}

function move_test_taker_pages(direction) {
    if(test_taker_page_idx == 0 && direction == -1) {
        return
    }

    if(test_taker_page_idx + 1 == pages.length && direction == 1) {
        return
    }

    test_taker_page_idx += direction

    if(test_taker_page_idx == 0) {
        test_taker_prev_page_btn.setAttribute("disabled", "")
    }

    else {
        test_taker_prev_page_btn.removeAttribute("disabled")
    }

    for(const page of pages) {
        page.style.transform = `translateX(${100 * test_taker_page_idx * -1}%)`
    }
}

function select_option(option_idx, question_idx) {
    let neighbouring_option_btns = document.getElementsByClassName(`question-${ question_idx }-options`)
    for(const option_btn of neighbouring_option_btns) {
        option_btn.classList.remove("bg-green-600")
        option_btn.classList.add("text-black")
        option_btn.classList.remove("text-white")
    }

    let selected_btn = document.getElementById(`question-${ question_idx }-option-${ option_idx }`)
    selected_btn.classList.add("bg-green-600")
    selected_btn.classList.add("text-white")
    selected_btn.classList.remove("text-black")

    selected_options[`${question_idx}`] = option_idx
}

function submit_test() {
    fetch(
        `/api_submit_test?token=${localStorage.getItem("token")}`,
        {
            method: "POST",
            body: JSON.stringify(selected_options),
            headers: {
                "Content-type": "application/json; charset=UTF-8"
            }
        }
    ).then(async function(resp) {
        if(resp.status == 200) {
            alert("Successfuly submitted test.")
            location.href = `/api_dashboard?token=${localStorage.getItem("token")}`
        }

        else {
            await resp.text().then(function(text) {
                alert(text)
            })
        }
    })
}

function handle_test_time(minutes) {
    const holder = document.getElementById("seconds-left")
    let sec = (minutes * 60) - 15
    
    setInterval(function() {
        sec -= 1
        holder.innerText = sec
        if(sec < 0) {
            submit_test()
            return
        }
    }, 1000)
}