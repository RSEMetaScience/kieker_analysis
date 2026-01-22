from enum import Enum


class GraphStyle(Enum):
    default = "default"
    usr_role = "usr_role"

    @property
    def value(self):
        if self == GraphStyle.usr_role:
            return [
                    {
                        "selector": "node",
                        "style": {  "label": "data(label)",
                                    "font-size": "10px",
                                    "text-valign": "center",
                                    "text-halign": "center",
                                    "text-rotation": "autorotate",
                                    "color": "black"
                        }
                    },
                {"selector": "node[rdf_type_str *= 'prov#Agent']", "style": {"label": "data(label)"}},
                {"selector": "node[rdf_type_str *= 'prov#Role']", "style": {"label": "data(label)"}},
                {
                    "selector": "edge",
                    "style": {"line-color": "#666",
                              "width": 1,
                              "label": "data(label)",
                              "font-size": "8px",
                              "color": "black"
                              }
                },

                    {
                        "selector": "node[rdf_type_str *= 'prov#Entity']",
                        "style": {"background-color": "#6baed6"}
                    },
                    {
                        "selector": "node[rdf_type_str *= 'prov#Activity']",
                        "style": {"background-color": "#fd8d3c"}
                    },
                    {
                        "selector": "node[rdf_type_str *= 'prov#Agent']",
                        "style": {"background-color": "#74c476"}
                    } ,               {
                    "selector": "node[format = 'inner']",
                    "style": {"background-color": "#6baed6",
                              "width": "data(size)",
                              "height": "data(size)"}
                }
                ]

        if self == GraphStyle.default:
            return [
    {
        "selector": "node",
        "style": {
            "label": "data(label)",
            "font-size": "10px",
            "text-valign": "center",
            "text-halign": "center",
             "text-rotation": "autorotate",
            "color": "black"
        }
    },
    {
        "selector": "edge",
        "style": {
            "label": "data(label)",
            "font-size": "8px",
            "color": "black"
        }
    },
    {
        "selector": "node[format *= 'outer']",
        "style": {"background-color": "#6baed6"}
    },

    {
        "selector": "node[rdf_type_str *= 'prov#Entity']",
        "style": {"background-color": "#6baed6"}
    },
    {
        "selector": "node[rdf_type_str *= 'prov#Activity']",
        "style": {"background-color": "#fd8d3c"}
    },
    {
        "selector": "node[rdf_type_str *= 'prov#Agent']",
        "style": {"background-color": "#74c476"}
    }
]

usr_role_styler = {
    "github2prov":"outer",
    "kieker-monitoring":"inner"
}