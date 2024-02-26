const documentation = document.getElementById("documentation")

documentation.addEventListener('click',()=>{
    const docBox = new WinBox({
        title: 'Documentation',
        class: ["no-full"],
        width:'400px',
        height:'400px',
        background: '#003060',
        top:50,
        right:50,
        bottom:50,
        left:50,
        border: 2,
        mount: document.getElementById("content").cloneNode(true),
        index: 1001
    })
})