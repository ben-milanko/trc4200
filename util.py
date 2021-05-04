import json

CONFIG_FILENAME = "config.json"
DEFAULT_CAM_URLS = {
    'pizzeria': "https://youtu.be/1EiC9bvVGnk",
    'pub': "https://youtu.be/6aJXND_Lfk8",
    'square': "https://youtu.be/DoUOrTJbIu4"
}
DEFAULT_TEMPLATE = {
    'url': None,
    'transform': None,
    'correction': None
}


def _config_entry(name, cam_url=None, transform=None, dist_corr=None) -> dict:
    # Read existing config if it exists
    try:
        old_entry = read_config_entry(name)
    except KeyError:
        old_entry = {}

    new_entry = {}
    if cam_url:
        new_entry['url'] = cam_url
    if transform:
        new_entry['transform'] = transform
    if dist_corr:
        cam_mat, coeffs = dist_corr
        new_entry['correction'] = {
            'camMatrix': cam_mat,
            'distCoeffs': coeffs
        }

    return {**DEFAULT_TEMPLATE, **old_entry, **new_entry}


def _read_config() -> dict:
    try:
        with open(CONFIG_FILENAME, 'r') as config_file:
            conf = json.load(config_file)
    except FileNotFoundError:
        conf = {k: {**DEFAULT_TEMPLATE, 'url': v} for k, v in DEFAULT_CAM_URLS.items()}
    return conf


def read_config_entry(key) -> dict:
    conf = _read_config()
    return conf[key]


def write_config_entry(key, **kwargs):
    conf = _read_config()
    conf[key] = _config_entry(key, **kwargs)
    with open(CONFIG_FILENAME, 'w') as config_file:
        json.dump(conf, config_file, indent=2)
