/**
 * DocItem/Content - Uses Docusaurus official i18n
 */

import React from 'react';
import Content from '@theme-original/DocItem/Content';
import type { WrapperProps } from '@docusaurus/types';

type Props = WrapperProps<typeof Content>;

export default function DocItemContent(props: Props): JSX.Element {
  return <Content {...props} />;
}
