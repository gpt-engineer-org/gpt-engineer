'use client';
import NextLink, { LinkProps as NextLinkProps } from 'next/link';
import {
  CSSProperties,
  ComponentProps,
  PropsWithChildren,
  useMemo,
} from 'react';

export type NavLinkProps = NextLinkProps &
  PropsWithChildren & {
    styles?: CSSProperties;
    borderRadius?: ComponentProps<typeof NextLink>['style'];
  };

function NavLink({ children, styles, ...props }: NavLinkProps) {
  const memoizedStyles = useMemo(
    () => ({
      ...styles,
    }),
    [styles],
  );

  return (
    <NextLink style={memoizedStyles} {...props}>
      {children}
    </NextLink>
  );
}

export default NavLink;
