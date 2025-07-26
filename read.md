# 🔐 thcoicrstch-landing-page

This repository is intended for the landing page of this hybrid cryptography and steganography system for securing sensitive image metadata. 
---

## Instructions
### Setup
1. Clone this repository to your Github Desktop
2. If you haven't downloaded `node.js`, please download v20.11.1. Access the download link here: https://nodejs.org/en
3. Open VS Code and open the terminal.
4. Make sure that you're accessing the `thchoish-lp` folder.
   - cd thchoish-lp
6. Type `npm start` to run the landing page.

### HTML/CSS Navigation (Note to Frontend Developers @Licelle @Mark)
1. The `thchoish-lp` has three(3) main folders (public, src, and node_modules). Go to the `public` folder.
2. Access the `index.html`, and `index.css` in the `public` folder. Write there your codes for the landing page design and functionality.


### Route (Note to System Integration Developer @Vhilly)
1. Access the `src` folder and modify the `App.js` to ensure that the landing page from the modified `index.html` is displaying. 
2. Configure the `Dockerfile` to satisfy the following:
   - Ensure it builds the React app and serves it via a web server (NGINX)
   - Include your .exe download inside the server so users can access it

