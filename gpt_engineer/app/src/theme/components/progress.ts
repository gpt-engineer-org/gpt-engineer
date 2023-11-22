import { mode } from '@chakra-ui/theme-tools';
export const progressStyles = {
	components: {
		Progress: {
			baseStyle: {
				field: {
					fontWeight: 400,
					w: '16px',
					h: '16px',
					borderRadius: '20px',
					_checked: { transform: 'translate(20px, 0px)' }
				},
				track: {
					w: '40px',
					h: '20px',
					borderRadius: '20px',
					_focus: {
						boxShadow: 'none'
					}
				}
			},

			variants: {
				table: (props: any) => ({
					field: {
						bg: 'brand.500',
						borderRadius: '16px',
						fontSize: 'sm'
					},
					track: {
						borderRadius: '20px',
						bg: mode('blue.50', 'whiteAlpha.50')(props),
						h: '8px',
						w: '54px'
					},
					thumb: {
						w: '250px'
					}
				})
			}
		}
	}
};
