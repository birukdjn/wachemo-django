$("#contactForm").validate({
    rules: {
        name: "required",
        email: {
            required: true,
            email: true
        },
        message: "required"
    },
    messages: {
        name: "Please enter your name",
        email: "Please enter a valid email address",
        message: "Please enter your message"
    },
    submitHandler: function(form) {
        // AJAX form submission logic here
        alert("Form submitted successfully!");
        form.reset();
    }
});