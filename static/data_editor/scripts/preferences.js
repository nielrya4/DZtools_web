const preferences = document.getElementById("preferences")

preferences.addEventListener('click',()=>{
    const docBox = new WinBox({
        title: 'Preferences',
        class: ["no-full"],
        width:'400px',
        height:'400px',
        background: 'lightslategray',
        top:50,
        right:50,
        bottom:50,
        left:50,
        border: 2,
        mount: document.getElementById("preferences_content").cloneNode(true),
        index: 1001
    })
})