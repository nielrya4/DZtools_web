        // Adjust the navbar width based on the content width
        function adjustNavbarWidth() {
        var contentWidth = document.documentElement.scrollWidth || document.body.scrollWidth;
        document.getElementById('nbar').style.width = contentWidth + 50 + 'px';
        }

        // Call the function initially and on window resize
        window.addEventListener('resize', adjustNavbarWidth);
        adjustNavbarWidth();