'use client'
import { Flex } from '@chakra-ui/react';

export default function IconBox(props: { icon: JSX.Element | string; [x: string]: any }) {
	const { icon, ...rest } = props;

	return (
        <Flex
            alignItems={'center'}
            justifyContent={'center'}
            borderRadius={'50%'}
            {...rest}
        >
            {icon}
        </Flex>
    );
}
