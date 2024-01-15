var test_creator_page_idx = 0
var test_creator_page_count = 1
var test_creator_pages_container = document.getElementById("test-creator-container")
var test_creator_prev_page_btn = document.getElementById("test-creator-prev-page-btn")

function create_test_creator_question_page() {
	test_creator_page_count++

	let new_page = document.getElementsByClassName("test-creator-question-page")[0].cloneNode(true)
	new_page.setAttribute("id", `test-creator-question-page-${test_creator_page_count}`)
	new_page.getElementsByClassName("test-creator-add-option-btn")[0].setAttribute("onclick", `test_creator_add_option('test-creator-options-container-${test_creator_page_count}')`)
	let options_container = new_page.getElementsByClassName("test-creator-options-container")[0]
	options_container.setAttribute("id", `test-creator-options-container-${test_creator_page_count}`)

	new_page.getElementsByClassName("test-creator-question-input")[0].value = ""
	new_page.getElementsByClassName("test-creator-correct-option-input")[0].value = ""
	new_page.getElementsByClassName("test-creator-options-container")[0].innerHTML = ""

	new_page.classList.add("animate-fade-in")
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
	option_num.className = "test-creator-option-number margin-small padding-small font-medium border-thin-black rounded-corners min-width"

	let option_input = document.createElement("input")
	option_input.className = "test-creator-option-input padding-medium font-small"
	option_input.placeholder = "Enter An Option"

	options_container.appendChild(option_num)
	options_container.appendChild(option_input)
	options_container.appendChild(document.createElement("br"))
}

function publish_test() {
	let metadata_page = document.getElementById("test-creator-metadata-page")

	let metadata = {}

	for(const input of metadata_page.getElementsByClassName("test-creator-metadata-input")) {
		let key = input.getAttribute("name")
		let value = input.value
		if(value == "") {
			alert("Did not publish test as one or more of the metadata fields was left empty.")
			return
		}

		metadata[key] = value
	}

	let questions = []
	let questions_idx = 0

	for(const question_page of document.getElementsByClassName("test-creator-question-page")) {
		let question = question_page.getElementsByClassName("test-creator-question-input")[0].value
		if(question == "") {
			alert("One of the questions was missing a question sentence. Test was not published.")
			return
		}

		let options = Array.from(question_page.getElementsByClassName("test-creator-option-input")).map(function(option_DOM) {
			return option_DOM.value
		})

		if(options.length == 0) {
			alert("One of the questions was missing options. Test was not published")
			return
		}
		
		let correct_option_idx = question_page.getElementsByClassName("test-creator-correct-option-input")[0].value
		if(correct_option_idx == "" || parseInt(correct_option_idx) > options.length || parseInt(correct_option_idx) < 1) {
			alert("One of the questions was either missing a correct answer or an invalid correct answer was entered.")
			return
		}

		questions.push({
			"question": question, 
			"options": options,
			"correct_option": correct_option_idx
		})
		questions_idx++
	}

	let data = {
		"metadata": metadata,
		"questions": questions
	}

	fetch(`${location.origin}/api_create_test?token=${localStorage.getItem("token")}`, {
		method: "POST",
		body: JSON.stringify(data),
		headers: {
			"Content-type": "application/json; charset=UTF-8"
		}
	}).then(function(resp) {
		if(resp.status == 200) {
			alert("Successfully published test to students.")
			location.href = "/"
		}

		else {
			alert("The test failed to publish. Please try again.")
			location.href = `/api_create_test?token=${localStorage.getItem("token")}`
		}
	})
}
