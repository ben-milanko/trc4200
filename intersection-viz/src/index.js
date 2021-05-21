import {Application} from "@pixi/app";
import {BatchRenderer, Renderer, RenderTexture, Texture} from "@pixi/core";
import {TickerPlugin} from "@pixi/ticker";
import {AppLoaderPlugin} from "@pixi/loaders";
import {BlurFilter} from "@pixi/filter-blur";
import {Sprite} from "@pixi/sprite";
import * as settings from "@pixi/settings";

import car_red from "../resources/assets/car_red.png";
import pedestrian from "../resources/assets/pedestrian.png";
import aerial from "../resources/assets/aerial.png";

Renderer.registerPlugin("batch", BatchRenderer);
Application.registerPlugin(TickerPlugin);
Application.registerPlugin(AppLoaderPlugin);

// App with width and height of the page
const displayHolder = document.querySelector("#display");
const app = new Application({resizeTo: displayHolder, resizeThrottle: 100});
displayHolder.appendChild(app.view); // Create Canvas tag in the body

let detections = {};
let sprites = {};
let heatMapSprites = [];
const SPRITE_TIMEOUT_MS = 500;
const bgSprite = Sprite.from(aerial);

function makeSprite(label) {
    let label_mapping = {
        0: () => Sprite.from(pedestrian),
        1: () => Sprite.from("bicycle"),
        2: () => Sprite.from(car_red),
        3: () => Sprite.from("motorcycle"),
        5: () => Sprite.from("bus"),
        7: () => Sprite.from("truck"),
        9: () => Sprite.from("traffic_light"),
        10: () => Sprite.from("fire_hydrant"),
        11: () => Sprite.from("stop_sign"),
        12: () => Sprite.from("parking_meter")
    };
    const newSprite = label_mapping[label]();
    newSprite.anchor.set(0.5); // We want to rotate our sprite relative to the center, so 0.5
    newSprite.width *= 0.02;
    newSprite.height *= 0.02;
    return newSprite;
}

function makeBlurTex() {
    const W1 = 80;
    const H1 = 80;
    const W2 = 40;
    const H2 = 40;

    let tex = RenderTexture.create({width: W1, height: H1});
    let spr = new Sprite(Texture.WHITE);
    spr.tint = 0xff7300;  // orange
    spr.anchor.set(0.5);
    spr.width = W2;
    spr.height = H2;
    spr.position.set(W1 / 2, H1 / 2);
    spr.filters = [new BlurFilter(15)];
    app.renderer.render(spr, tex);
    return tex;
}

function makeBlurSprite(alpha) {
    let tex = makeBlurTex();
    let spr = new Sprite(tex);
    spr.alpha = alpha;
    return spr;
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
    sp.lastUpdated = Date.now();
    return sp;
}

function drawHeatMap() {
    // clear last heatmap
    for (let sp of heatMapSprites) {
        app.stage.removeChild(sp);
    }
    heatMapSprites = [];

    // for (let [id, obj] of Object.entries(detections)) {
    //     let blurSprite = makeBlurSprite(0.8);
    //     blurSprite.x = obj.x;
    //     blurSprite.y = obj.y;
    //     blurSprite.height = 100;
    //     blurSprite.width = 100;
    //     app.stage.addChild(blurSprite);
    //     heatMapSprites.push(blurSprite);
    // }
    // console.log(heatMapSprites);
}

// Load the logo
app.loader.add("car_red", car_red);
app.loader.load(() => {
    // draw background
    app.stage.addChild(bgSprite);

    app.renderer.resize(app.renderer.width, app.renderer.height);

    // websocket setup
    const ws = new WebSocket(`ws://${window.location.hostname}:8000/stream`);
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
        const ms = delta / settings.settings.TARGET_FPMS;
        for (let [id, sp] of Object.entries(sprites)) {
            // remove old sprites
            if (Date.now() - sp.lastUpdated > SPRITE_TIMEOUT_MS || !(id in detections)) {
                // console.warn("removed child");
                app.stage.removeChild(sp);
                delete sprites[id];
                continue;
            }

            // animate sprites on tick
            let [xVel, yVel] = detections[id].vel;
            sp.x += xVel * ms / 1000;
            sp.y += yVel * ms / 1000;
        }
        drawHeatMap();
    };

    // Put the rotating function into the update loop
    app.ticker.add(carUpdate);
});

app.renderer.on("resize", (width, height) => {
    let scale = Math.min(height / bgSprite.height, width / bgSprite.width);
    app.stage.setTransform((width - bgSprite.width * scale) / 2, 0, scale, scale);
});
