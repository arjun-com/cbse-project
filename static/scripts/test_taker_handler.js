var test_taker_page_idx = 0
var test_taker_prev_page_btn = document.getElementById("test-taker-prev-page-btn")
var test_taker_option_btns = document.getElementsByClassName("test-taker-option-btn")
var pages = document.getElementsByClassName("test-taker-page")

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