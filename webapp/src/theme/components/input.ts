import { mode } from '@chakra-ui/theme-tools';
export const inputStyles = {
  components: {
    Input: {
      baseStyle: {
        field: {
          fontWeight: 400,
          borderRadius: '14px',
        },
      },

      variants: {
        main: (props: any) => ({
          field: {
            bg: mode('transparent', 'navy.800')(props),
            border: '1px solid',
            color: mode('navy.700', 'white')(props),
            borderColor: mode('gray.200', 'whiteAlpha.100')(props),
            borderRadius: '12px',
            fontSize: 'sm',
            p: '20px',
            _placeholder: { color: 'secondaryGray.400' },
          },
        }),
        auth: (props: any) => ({
          field: {
            fontWeight: '500',
            color: mode('navy.700', 'white')(props),
            bg: mode('transparent', 'transparent')(props),
            border: '1px solid',
            borderColor: mode('gray.200', 'rgba(135, 140, 189, 0.3)')(props),
            borderRadius: '12px',
            _placeholder: {
              color: 'gray.500',
              fontWeight: '400',
            },
          },
        }),
        authSecondary: () => ({
          field: {
            bg: 'transparent',
            border: '1px solid',
            borderColor: 'gray.200',
            borderRadius: '12px',
            _placeholder: { color: 'gray.500' },
          },
        }),
        search: () => ({
          field: {
            border: 'none',
            py: '11px',
            borderRadius: 'inherit',
            _placeholder: { color: 'gray.500' },
          },
        }),
      },
    },
    NumberInput: {
      baseStyle: {
        field: {
          fontWeight: 400,
        },
      },

      variants: {
        main: () => ({
          field: {
            bg: 'transparent',
            border: '1px solid',

            borderColor: 'gray.200',
            borderRadius: '12px',
            _placeholder: { color: 'gray.500' },
          },
        }),
        auth: () => ({
          field: {
            bg: 'transparent',
            border: '1px solid',

            borderColor: 'gray.200',
            borderRadius: '12px',
            _placeholder: { color: 'gray.500' },
          },
        }),
        authSecondary: () => ({
          field: {
            bg: 'transparent',
            border: '1px solid',

            borderColor: 'gray.200',
            borderRadius: '12px',
            _placeholder: { color: 'gray.500' },
          },
        }),
        search: () => ({
          field: {
            border: 'none',
            py: '11px',
            borderRadius: 'inherit',
            _placeholder: { color: 'gray.500' },
          },
        }),
      },
    },
    Select: {
      baseStyle: {
        field: {
          fontWeight: 500,
        },
      },

      variants: {
        main: (props: any) => ({
          field: {
            bg: mode('transparent', 'navy.800')(props),
            border: '1px solid',
            color: 'gray.500',
            borderColor: mode('gray.200', 'whiteAlpha.100')(props),
            borderRadius: '12px',
            _placeholder: { color: 'navy.700' },
          },
          icon: {
            color: 'gray.500',
          },
        }),
        mini: (props: any) => ({
          field: {
            bg: mode('transparent', 'navy.800')(props),
            border: '0px solid transparent',
            fontSize: '0px',
            p: '10px',
            _placeholder: { color: 'navy.700' },
          },
          icon: {
            color: 'gray.500',
          },
        }),
        subtle: () => ({
          box: {
            width: 'unset',
          },
          field: {
            bg: 'transparent',
            border: '0px solid',
            color: 'gray.500',
            borderColor: 'transparent',
            width: 'max-content',
            _placeholder: { color: 'navy.700' },
          },
          icon: {
            color: 'gray.500',
          },
        }),
        transparent: (props: any) => ({
          field: {
            bg: 'transparent',
            border: '0px solid',
            width: 'min-content',
            color: mode('gray.500', 'gray.500')(props),
            borderColor: 'transparent',
            padding: '0px',
            paddingLeft: '8px',
            paddingRight: '20px',
            fontWeight: '700',
            fontSize: '14px',
            _placeholder: { color: 'navy.700' },
          },
          icon: {
            transform: 'none !important',
            position: 'unset !important',
            width: 'unset',
            color: 'gray.500',
            right: '0px',
          },
        }),
        auth: () => ({
          field: {
            bg: 'transparent',
            border: '1px solid',
            borderColor: 'gray.200',
            borderRadius: '12px',
            _placeholder: { color: 'navy.700' },
          },
        }),
        authSecondary: (props: any) => ({
          field: {
            bg: 'transparent',
            border: '1px solid',

            borderColor: 'gray.200',
            borderRadius: '12px',
            _placeholder: { color: 'navy.700' },
          },
        }),
        search: (props: any) => ({
          field: {
            border: 'none',
            py: '11px',
            borderRadius: 'inherit',
            _placeholder: { color: 'navy.700' },
          },
        }),
      },
    },
  },
};
