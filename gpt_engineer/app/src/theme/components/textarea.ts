import { mode } from '@chakra-ui/theme-tools';
export const textareaStyles = {
  components: {
    Textarea: {
      baseStyle: {
        field: {
          fontWeight: 400,
          borderRadius: '8px',
        },
      },

      variants: {
        main: (props: any) => ({
          field: {
            bg: mode('transparent', 'navy.800')(props),
            border: '1px solid !important',
            color: mode('navy.700', 'white')(props),
            borderColor: mode('gray.200', 'whiteAlpha.100')(props),
            borderRadius: '16px',
            fontSize: 'sm',
            p: '20px',
            _placeholder: { color: 'navy.700' },
          },
        }),
        auth: () => ({
          field: {
            bg: 'white',
            border: '1px solid',
            borderColor: 'gray.200',
            borderRadius: '16px',
            _placeholder: { color: 'gray.500' },
          },
        }),
        authSecondary: () => ({
          field: {
            bg: 'white',
            border: '1px solid',

            borderColor: 'gray.200',
            borderRadius: '16px',
            _placeholder: { color: 'navy.700' },
          },
        }),
        search: () => ({
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
