var test_creator_page_idx = 0
var test_creator_page_count = 1
var test_creator_pages_container = document.getElementById("test-creator-container")
var test_creator_prev_page_btn = document.getElementById("test-creator-prev-page-btn")

function create_test_creator_question_page() {
	test_creator_page_count++

	let new_page = document.getElementsByClassName("test-creator-question-page")[0].cloneNode(true)
	new_page.setAttribute("id", `test-creator-question-page-${test_creator_page_count}`)
	new_page.getElementsByClassName("test-creator-add-option-btn")[0].setAttribute("onclick", `test_creator_add_option('test-creator-options-container-${test_creator_page_count}')`)
	new_page.getElementsByClassName("test-creator-options-container")[0].setAttribute("id", `test-creator-options-container-${test_creator_page_count}`)

	test_creator_pages_container.appendChild(new_page)
}

function move_test_creator_pages(direction) { // if direction is +1 it means forward if -1 it means backward.
	test_creator_page_idx += direction

	if(test_creator_page_idx == 0) {
		test_creator_prev_page_btn.setAttribute("disabled", "")
	}

	else if(test_creator_page_idx == 1 && direction == 1) {
		test_creator_prev_page_btn.removeAttribute("disabled", "")
	}

	const pages = document.getElementsByClassName("test-creator-page")
	for(const page of pages) {
		page.style.transform = `translateX(${test_creator_page_idx * 100 * -1}%)`
	}

	if(test_creator_page_idx > test_creator_page_count) {
		create_test_creator_question_page()
	}
}

function test_creator_add_option(options_container_id) {
	const options_container = document.getElementById(options_container_id)

	if(options_container.getElementsByClassName("test-creator-option-input") != null && options_container.getElementsByClassName("test-creator-option-input").length >= 4) {
		alert("You can have a maximum of 4 options per question.")
		return
	}

	let option_num = document.createElement("p")
	option_num.innerText = options_container.getElementsByClassName("test-creator-option-input").length == null ? 1 : options_container.getElementsByClassName("test-creator-option-input").length + 1
	option_num.className = "margin-small padding-small font-medium border-thin-black rounded-corners min-width"

	let option_input = document.createElement("input")
	option_input.className = "test-creator-option-input padding-medium font-small"
	option_input.placeholder = "Enter An Option"

	options_container.appendChild(option_num)
	options_container.appendChild(option_input)
	options_container.appendChild(document.createElement("br"))
}
