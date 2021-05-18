// Import Application class that is the main part of our PIXI project
import {Application} from "@pixi/app";

// In order that PIXI could render things we need to register appropriate plugins
import {BatchRenderer, Renderer} from "@pixi/core"; // BatchRenderer is the "plugin" for drawing sprites // Renderer is the class that is going to register plugins
import {TickerPlugin} from "@pixi/ticker"; // TickerPlugin is the plugin for running an update loop (it's for the application class)
// And just for convenience let's register Loader plugin in order to use it right from Application instance like app.loader.add(..) etc.
import {AppLoaderPlugin} from "@pixi/loaders";
// Sprite is our image on the stage
import {Sprite} from "@pixi/sprite";

import car_red from "../resources/assets/car_red.png";

Renderer.registerPlugin("batch", BatchRenderer);

Application.registerPlugin(TickerPlugin);

Application.registerPlugin(AppLoaderPlugin);

// App with width and height of the page
const app = new Application({
    width: window.innerWidth,
    height: window.innerHeight
});
document.body.appendChild(app.view); // Create Canvas tag in the body

let detections = {};
let sprites = {};

function makeSprite(label) {
    // TODO: choose sprite depending on label
    const carSprite = Sprite.from("car_red");
    carSprite.anchor.set(0.5); // We want to rotate our sprite relative to the center, so 0.5
    carSprite.width *= 0.05;
    carSprite.height *= 0.05;
    return carSprite;
}

function updateOrCreateSprite(id, data) {
    if (!(id in sprites)) {
        // create new sprite
        let s = makeSprite(data.objType);
        app.stage.addChild(s);
        sprites[id] = s;
    }
    let sp = sprites[id];
    [sp.x, sp.y] = data.location;
    sp.rotation = data.rotation;
    // TODO: handle velocity
    return sp;
}

// Load the logo
app.loader.add("car_red", car_red);
app.loader.load(() => {
    // websocket setup
    const ws = new WebSocket("ws://localhost:8000/stream");
    ws.onmessage = (ev) => {
        let ev_data = JSON.parse(ev.data);

        if (ev_data.type !== "TRACKING") {
            console.log(ev_data);
            return;
        }

        detections = ev_data.data;
        for (let [id, obj] of Object.entries(detections)) {
            updateOrCreateSprite(id, obj);
        }
    };

    const carUpdate = function (delta) {
        carSprite.rotation += 0.8 * (Math.random() - 0.5) * delta;
        carSprite.x += 10 * (Math.random() - 0.5) * delta;
        carSprite.y += 10 * (Math.random() - 0.5) * delta;
    };

    // Put the rotating function into the update loop
    // app.ticker.add(carUpdate);
});
