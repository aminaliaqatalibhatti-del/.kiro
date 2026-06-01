function selectOption(category, element) {
    // 1. Get the parent group (the row of buttons)
    const parent = element.parentElement;
    
    // 2. Remove 'selected' class from all buttons in this specific group
    const siblings = parent.querySelectorAll('.option');
    siblings.forEach(btn => btn.classList.remove('selected'));
    
    // 3. Add 'selected' to the one you clicked
    element.classList.add('selected');
    
    // 4. Update the hidden input value for the API
    document.getElementById(category).value = element.getAttribute('data-value');
    
    console.log(`Updated ${category} to ${element.getAttribute('data-value')}`);
}

//Function to slide/fade between our pages
function showPage(pageId){
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    document.getElementById(pageId).classList.add('active');
    if (pageId === 'saved-page' && typeof loadSavedStories === 'function') {
        loadSavedStories();
    }
}

async function generateJourney() {
    const mood = document.getElementById("mood").value;
    startDynamicMusic(mood);

    const display = document.getElementById("story-display");
    const storyImg = document.getElementById("story-image");
    
    // Grab the values currently stored in the hidden inputs
    const personality = document.getElementById("personality").value;
    const budget = document.getElementById("budget").value;
    const preference = document.getElementById("preference").value;

    display.innerText = "Consulting the stars and composing your destiny...";
    storyImg.style.display = "none";
    showPage('story-page');

    try {
        const response = await fetch(
            `/get_story?personality=${personality}&mood=${mood}&budget=${budget}&preference=${preference}`
        );
        const data = await response.json();
        display.innerText = data.story;
        storyImg.src = `/static/images/${encodeURIComponent(data.image)}`;
        storyImg.style.display = "block";
        // Attempt to save the generated story on the server
        try {
            const saveResp = await fetch('/save_story', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ story: data.story, image: data.image })
            });
            const saveData = await saveResp.json();
            if (saveData.status === 'success') {
                // remove any previous link
                const old = document.getElementById('save-link');
                if (old) old.remove();
                const a = document.createElement('a');
                a.id = 'save-link';
                a.href = saveData.url;
                a.innerText = 'Download saved story';
                a.target = '_blank';
                display.appendChild(document.createElement('br'));
                display.appendChild(a);
                // Refresh the saved stories list on the main page
                if (typeof loadSavedStories === 'function') loadSavedStories();
            }
        } catch (err) {
            console.log('Save request failed:', err);
        }
    } catch (error) {
        display.innerText = "Connection lost. Is your Flask server running?";
        storyImg.style.display = "none";
    }
}
const music = document.getElementById("bg-music");
const musicBtn = document.getElementById("music-toggle");

function startDynamicMusic(moodValue) {
    // Files in /static/audio are .mpeg in this project
    let trackName = "peaceful.mpeg";
    if (moodValue === "1") {
        trackName = "peaceful.mpeg";
    } else if (moodValue === "2") {
        trackName = "mysterious.mpeg";
    } else if (moodValue === "3") {
        trackName = "dangerous.mpeg";
    } else if (moodValue === "4") {
        trackName = "despair.mpeg";
    }

    const trackUrl = `/static/audio/${trackName}`;

    if(!music.src.includes(trackUrl)) {
        music.src = trackUrl;
        music.load();
    }

    if (music.paused) {
        music.play().then(() => {
            musicBtn.innerText = "🎵 Music: On";
        }).catch(err => console.log("Audio play blocked initially: ", err));
    }
}

function toggleMusic() {
    if (music.src === "" || music.src === window.location.href) {
        // If music hasn't started yet, play the default peaceful track
        const mood = document.getElementById("mood").value;
        startDynamicMusic(mood);
        return;
    }

    if (music.paused) {
        music.play();
        musicBtn.innerText = "🎵 Music: On";
    } else {
        music.pause();
        musicBtn.innerText = "🎵 Music: Off"
    }
}

// Load saved stories and render into the saved-list element
async function loadSavedStories() {
    const container = document.getElementById('saved-list');
    if (!container) return;
    container.innerText = 'Loading saved stories...';
    try {
        const resp = await fetch('/list_stories');
        const data = await resp.json();
        if (data.status === 'success' && Array.isArray(data.files) && data.files.length) {
            container.innerHTML = '';
            data.files.forEach(f => {
                const row = document.createElement('div');
                row.className = 'saved-item-row';

                const a = document.createElement('a');
                a.href = f.url;
                a.innerText = f.name;
                a.target = '_blank';
                a.className = 'saved-story-link';

                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'delete-story-btn';
                btn.innerText = 'Delete';
                btn.onclick = async () => {
                    if (!confirm('Delete this saved story?')) return;
                    await deleteStory(f.name);
                };

                const left = document.createElement('div');
                left.appendChild(a);
                row.appendChild(left);
                row.appendChild(btn);
                container.appendChild(row);
            });
        } else {
            container.innerText = 'No saved stories yet.';
        }
    } catch (err) {
        container.innerText = 'Could not load saved stories.';
        console.log('loadSavedStories error', err);
    }
}

// Run on initial load so the saved stories page is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        document.getElementById('saved-list') && loadSavedStories();
    });
} else {
    document.getElementById('saved-list') && loadSavedStories();
}

async function deleteStory(filename) {
    try {
        const resp = await fetch('/delete_story', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename })
        });
        const data = await resp.json();
        if (data.status === 'success') {
            loadSavedStories();
        } else {
            alert('Delete failed: ' + (data.message || 'unknown'));
        }
    } catch (err) {
        console.log('deleteStory error', err);
        alert('Delete failed');
    }
}