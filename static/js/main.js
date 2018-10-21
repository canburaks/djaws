


function activeMenu() {
  var url = window.location.href;
  if (url.includes("dashboard")) {
    let element = document.getElementById("editorschoicepage");
    element.classList.add("active");
  }
  else if (url.includes("editor")) {
    let element = document.getElementById("editorschoicepage");
    element.classList.add("active");
  }
  else if (url.includes("movies/movies/")) {
    let element = document.getElementById("allmoviespage");
    element.classList.add("active");
  }
  else if (url.includes("imdb")) {
    let element = document.getElementById("imdbpage");
    element.classList.add("active");
  }
  else if (url.includes("users")) {
    let element = document.getElementById("userpage");
    element.classList.add("active");
  }
  else if (url.includes("login")) {
    let element = document.getElementById("loginpage");
    element.classList.add("active");
  }
  else if (url.includes("signup")) {
    let element = document.getElementById("signuppage");
    element.classList.add("active");
  }
}
activeMenu()

// progressbar.js@1.0.0 version is used
// Docs: http://progressbarjs.readthedocs.org/en/1.0.0/
/*

var bar = new ProgressBar.SemiCircle(container, {
  strokeWidth: 6,
  color: '#FFEA82',
  trailColor: '#eee',
  trailWidth: 8,
  easing: 'easeInOut',
  duration: 4900,
  svgStyle: null,
  text: {
    value: '',
    alignToBottom: false
  },
  from: {color: '#D12D40'},
  to: {color: '#1767E0'},
  // Set default step function for all animate calls
  step: (state, bar) => {
    bar.path.setAttribute('stroke', state.color);
    var value = (bar.value() * 5).toFixed(2);
    if (value === 0) {
      bar.setText('');
    } else {
      bar.setText(value);
    }

    bar.text.style.color = state.color;

  }
});
bar.text.style.fontFamily = '"Raleway", Helvetica, sans-serif';
bar.text.style.fontSize = '1rem';

bar.animate(average / 5);  // Number from 0.0 to 1.0
*/
