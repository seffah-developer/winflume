"""
WinFlume Pro Max - Flume Characteristics

Practical, plain-language guidance per flume family (not per size, since these
traits are consistent within a family). Grounded in Clemmens, Bos & Replogle
(2001) "Water Measurement with Flumes and Weirs" and the USBR Water Measurement
Manual, both in the project reference library.
"""

FLUME_CHARACTERISTICS = {
    "rbc": {
        "display_name": "RBC Flume",
        "best_for": "Earthen or unlined ditches, sites with sediment-laden flow, portable/seasonal installations",
        "sediment_handling": (
            "Designed specifically for low head loss and passing sediment through rather than "
            "trapping it - this was the core design goal behind the RBC (Replogle-Bos-Clemmens) "
            "flume. A good choice if your channel carries sand or silt."
        ),
        "recommended_channel_material": "Works well in earthen/unlined channels; also fine in concrete",
        "installation_notes": (
            "Portable and relatively easy to place in a dry channel bed. A cutoff sheet should be "
            "buried (~4 in / 0.1 m) at the upstream edge to prevent water from bypassing underneath."
        ),
    },
    "parshall": {
        "display_name": "Parshall Flume",
        "best_for": "Permanent or long-term installations, regulatory/compliance measurement, sites without heavy debris",
        "sediment_handling": (
            "The throat contraction speeds up the flow, which generally keeps normal sand and silt "
            "moving through rather than settling. However, heavy debris or high sediment loads can "
            "still cause problems - if your channel regularly carries a lot of debris, a Parshall "
            "flume may need more frequent maintenance than an RBC flume in the same conditions."
        ),
        "recommended_channel_material": "Well suited to concrete-lined channels; the ASTM-standardized "
        "design is widely accepted for accurate, long-term or regulatory measurement",
        "installation_notes": (
            "Needs a stable, level, watertight foundation. Larger sizes are typically built in place "
            "rather than dropped in as a single portable unit."
        ),
    },
    "trapezoidal_60deg_v": {
        "display_name": "60° V-Trapezoidal Flume",
        "best_for": "Small agricultural channels with a wide range of flow rates (both very low and higher flows)",
        "sediment_handling": (
            "No specific sediment-passing design feature - like most flumes, keeping head loss low "
            "and avoiding excess ponding upstream is the main way to prevent sediment settling."
        ),
        "recommended_channel_material": "Common in both earthen and lined small channels",
        "installation_notes": (
            "The V-notch shape gives good sensitivity at low flows while the wider top handles "
            "higher flows in the same structure - useful where flow varies a lot through the season."
        ),
    },
    "trapezoidal_45deg_wsc_no4": {
        "display_name": "WSC Trapezoidal Flume",
        "best_for": "Small agricultural channels, similar use case to the 60° V-Trapezoidal family",
        "sediment_handling": "No specific sediment-passing design feature - minimize head loss to reduce settling risk.",
        "recommended_channel_material": "Common in both earthen and lined small channels",
        "installation_notes": "Originally developed for small-channel agricultural flow measurement.",
    },
    "trapezoidal_38deg_srcrc_no2": {
        "display_name": "SRCRC Trapezoidal Flume",
        "best_for": "Larger agricultural or irrigation-district channels",
        "sediment_handling": "No specific sediment-passing design feature - minimize head loss to reduce settling risk.",
        "recommended_channel_material": "Common in both earthen and lined channels",
        "installation_notes": "Larger-capacity trapezoidal design for bigger channels than the WSC family.",
    },
    "trapezoidal_60deg": {
        "display_name": "60° Trapezoidal Flume",
        "best_for": "Mid-size agricultural channels",
        "sediment_handling": "No specific sediment-passing design feature - minimize head loss to reduce settling risk.",
        "recommended_channel_material": "Common in both earthen and lined channels",
        "installation_notes": "Mid-size option between the small WSC/V-notch sizes and the larger SRCRC sizes.",
    },
}


def get_characteristics(flume_type):
    return FLUME_CHARACTERISTICS.get(flume_type)
