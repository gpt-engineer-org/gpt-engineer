'use client';
import { Box } from '@chakra-ui/react';

export const renderTrack = ({ style, ...props }: any) => {
  const trackStyle = {
    position: 'absolute',
    maxWidth: '100%',
    transition: 'opacity 200ms ease 0s',
    opacity: 0,
    background: 'transparent',
    bottom: 2,
    top: 2,
    borderRadius: 3,
    right: 0,
  };
  return <div style={{ ...style, ...trackStyle }} {...props} />;
};
export const renderThumb = ({ style, ...props }: any) => {
  const thumbStyle = {
    borderRadius: 15,
    background: 'rgba(222, 222, 222, .1)',
  };
  return <div style={{ ...style, ...thumbStyle }} {...props} />;
};
export const renderView = ({ style, ...props }: any) => {
  const viewStyle = {
    marginBottom: -22,
  };
  return (
    <Box
      me={{ base: '0px !important', lg: '-16px !important' }}
      style={{ ...style, ...viewStyle }}
      {...props}
    />
  );
};
