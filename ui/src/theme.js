import { createTheme } from "@mui/material/styles";

const theme = createTheme({
    palette: {
        type: 'light',
        primary: {
          main: '#455a64',
        },
        secondary: {
          main: '#c93f3f',
        },
        error: {
          main: '#ff3d00',
        },
        warning: {
          main: '#fb8c00',
        },
        background: {
          default: '#f0f0f0',
          paper: '#fafafa',
        },
      },
      shape: {
        borderRadius: 0,
      },
      props: {
        MuiTooltip: {
          arrow: true,
        },
        
      },
    typography: {
        statblockTitle: {
          fontFamily:"Mr Eaves Small Caps",
          fontSize:34,
          lineHeight:1
        },
        statblockRaceType: {
          fontFamily:"Scaly Sans",
          fontStyle:"italic",
          fontSize:16,
          lineHeight:1
        },
        statblock: {
          fontFamily:"Scaly Sans",
          fontSize:17,
          lineHeight:1.1
        },
        statblockTable: {
          fontFamily:"Scaly Sans",
          fontSize:18,
          lineHeight:1
        },
        statblockSection: {
          fontFamily:"Scaly Sans Caps",
          fontSize:24
        },
        statblockDescription: {
          fontFamily:"Bookinsanity Remake",
          fontSize:18
        },
        nav: {
          fontFamily:"Scaly Sans Caps",
          fontSize:18
        },
        logo: {
          fontFamily:"Scaly Sans",
          fontSize:34
        },
        pageTitle: {
          fontFamily:"Scaly Sans Caps",
          fontSize:40,
          lineHeight:1
        },
        pageSubtitle: {
          fontFamily:"Scaly Sans Caps",
          fontSize:30,
          lineHeight:1
        },
        button: {
          textTransform: 'none',
          fontFamily:"Scaly Sans",
          fontSize:16,
          lineHeight:1
        }

    },

    components: {
        MuiPaper: {
            defaultProps: {
                square:false,
                variant:"elevation",
                elevation:1
                //variant:"outlined"
            }
        },
        MuiButton: {
            defaultProps: {
                variant:"contained",
                elevation:1
            },
            styleOverrides: {
                root: {
                  borderRadius: 0
                }
              }
        },
        MuiListItem: {
            root: {
              "&:selected": {
                backgroundColor: "red",
                "&:hover": {
                  backgroundColor: "orange",
                },
              },
            },
        },
    }
});
console.log(theme);
export default theme;