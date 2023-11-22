import { mode } from '@chakra-ui/theme-tools';
export const switchStyles = {
    components: {
        Switch: {
            baseStyle: {
                thumb: {
                    fontWeight: 400,
                    borderRadius: '50%',
                    w: '16px',
                    h: '16px',
                    _checked: { transform: 'translate(20px, 0px)' },
                },
                track: {
                    display: 'flex',
                    alignItems: 'center',
                    boxSizing: 'border-box',
                    w: '40px',
                    h: '20px',
                    p: '2px',
                    ps: '2px',
                    _focus: {
                        boxShadow: 'none',
                    },
                },
            },

            variants: {
                main: (props: any) => ({
                    track: {
                        bg: mode('gray.300', 'navy.700')(props),
                    },
                }),
            },
        },
    },
};
