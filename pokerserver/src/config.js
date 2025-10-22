var r = document.querySelector(':root');

export const API_BASE = "http://localhost:8000/api"; // change to your backend address

function myFunction_get() {
  // Get the styles (properties and values) for the root
  var rs = getComputedStyle(r);
  // Alert the value of the --primary-bg-color variable
  alert("The value of --primary-bg-color is: " + rs.getPropertyValue('--primary-bg-color'));
}

// Function for setting a variable value
function myFunction_set() {
  // Set the value of variable --primary-bg-color to another value (in this case "green")
  r.style.setProperty('--primary-bg-color', 'green');
}
