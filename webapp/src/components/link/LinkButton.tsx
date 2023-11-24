'use client';
import Link, { LinkProps } from 'next/link';
import { Button, ButtonProps } from '@chakra-ui/react';

type ChakraAndNextProps = ButtonProps & LinkProps;

export default function LinkButton({
  href,
  children,
  prefetch = true,
  ...props
}: ChakraAndNextProps) {
  return (
    <Link href={href} passHref prefetch={prefetch}>
      <Button as="a" variant="a" {...props}>
        {children}
      </Button>
    </Link>
  );
}
