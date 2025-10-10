import { z } from 'zod';

/**
 * Any array of ToolDefinitions.
 */
export type TAnyToolDefinitionArray = Array<
  ToolDefinition<string, z.AnyZodObject>
>;

/**
 * A map of ToolDefinitions, indexed by name.
 */
export type TAnyToolDefinitionMap = Readonly<{
  [K in string]: ToolDefinition<any, any>;
}>;

/**
 * Helper type to create a map of ToolDefinitions, indexed by name, from an array of ToolDefinitions.
 */
export type TToolDefinitionMap<
  TToolDefinitionArray extends TAnyToolDefinitionArray,
> = TToolDefinitionArray extends [infer TFirst, ...infer Rest]
  ? TFirst extends TAnyToolDefinitionArray[number]
    ? Rest extends TAnyToolDefinitionArray
      ? Readonly<{ [K in TFirst['name']]: TFirst }> & TToolDefinitionMap<Rest>
      : never
    : never
  : Readonly<{}>;

/**
 * A tool definition contains all information required for a language model to generate tool calls.
 */
export interface ToolDefinition<
  NAME extends string,
  PARAMETERS extends z.AnyZodObject,
> {
  /**
   * The name of the tool.
   * Should be understandable for language models and unique among the tools that they know.
   *
   * Note: Using generics to enable result type inference when there are multiple tool calls.
   */
  name: NAME;

  /**
   * A optional description of what the tool does. Will be used by the language model to decide whether to use the tool.
   */
  description?: string;

  /**
   * The schema of the input that the tool expects. The language model will use this to generate the input.
   * Use descriptions to make the input understandable for the language model.
   */
  parameters: PARAMETERS;
}
