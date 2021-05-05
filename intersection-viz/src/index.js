// Import Application class that is the main part of our PIXI project
import {Application} from "@pixi/app";

// In order that PIXI could render things we need to register appropriate plugins
import {BatchRenderer, Renderer} from "@pixi/core"; // BatchRenderer is the "plugin" for drawing sprites // Renderer is the class that is going to register plugins
import {TickerPlugin} from "@pixi/ticker"; // TickerPlugin is the plugin for running an update loop (it's for the application class)
// And just for convenience let's register Loader plugin in order to use it right from Application instance like app.loader.add(..) etc.
import {AppLoaderPlugin} from "@pixi/loaders";
// Sprite is our image on the stage
import {Sprite} from "@pixi/sprite";

import bunny from "../resources/assets/bunny.png";

Renderer.registerPlugin("batch", BatchRenderer);

Application.registerPlugin(TickerPlugin);

Application.registerPlugin(AppLoaderPlugin);

// App with width and height of the page
const app = new Application({
    width: window.innerWidth,
    height: window.innerHeight
});
document.body.appendChild(app.view); // Create Canvas tag in the body

// Load the logo
app.loader.add("car", bunny);
app.loader.load(() => {
    const carSprite = Sprite.from("car");
    carSprite.anchor.set(0.5); // We want to rotate our sprite relative to the center, so 0.5
    app.stage.addChild(carSprite);

    // Position the sprite at the center of the stage
    carSprite.x = app.screen.width * 0.5;
    carSprite.y = app.screen.height * 0.5;

    const carUpdate = function (delta) {
        carSprite.rotation += 0.8 * (Math.random() - 0.5) * delta;
        carSprite.x += 10 * (Math.random() - 0.5) * delta;
        carSprite.y += 10 * (Math.random() - 0.5) * delta;
        carSprite.width += 30 * (Math.random() - 0.48) * delta;
        carSprite.height += 30 * (Math.random() - 0.48) * delta;
    };

    // Put the rotating function into the update loop
    app.ticker.add(carUpdate);
});
