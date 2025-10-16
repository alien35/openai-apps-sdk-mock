import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import { URL } from "node:url";

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";
import {
  CallToolRequestSchema,
  ListResourceTemplatesRequestSchema,
  ListResourcesRequestSchema,
  ListToolsRequestSchema,
  ReadResourceRequestSchema,
  type CallToolRequest,
  type ListResourceTemplatesRequest,
  type ListResourcesRequest,
  type ListToolsRequest,
  type ReadResourceRequest,
  type Resource,
  type ResourceTemplate,
  type Tool
} from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";
import { INSURANCE_STATE_WIDGET_HTML } from "./insurance-state-widget.js";

type PizzazWidget = {
  id: string;
  title: string;
  templateUri: string;
  invoking: string;
  invoked: string;
  html: string;
  responseText: string;
  inputSchema: Tool["inputSchema"];
  toolDescription?: string;
};

function widgetMeta(widget: PizzazWidget) {
  return {
    "openai/outputTemplate": widget.templateUri,
    "openai/toolInvocation/invoking": widget.invoking,
    "openai/toolInvocation/invoked": widget.invoked,
    "openai/widgetAccessible": true,
    "openai/resultCanProduceWidget": true
  } as const;
}

const pizzaToolInputSchema = {
  type: "object",
  properties: {
    pizzaTopping: {
      type: "string",
      description: "Topping to mention when rendering the widget.",
    },
  },
  required: ["pizzaTopping"],
  additionalProperties: false,
} as const;

const pizzaToolInputParser = z.object({
  pizzaTopping: z.string(),
});

const insuranceStateInputSchema = {
  type: "object",
  properties: {
    state: {
      type: "string",
      description:
        "Two-letter U.S. state or District of Columbia abbreviation (for example, \"CA\").",
      minLength: 2,
      maxLength: 2,
      pattern: "^[A-Za-z]{2}$",
    },
  },
  required: [],
  additionalProperties: false,
} as const;

const insuranceStateParser = z
  .object({
    state: z
      .string()
      .trim()
      .min(2)
      .max(2)
      .regex(/^[A-Za-z]{2}$/)
      .transform((value) => value.toUpperCase())
      .optional(),
  })
  .strict();

const widgets: PizzazWidget[] = [
  {
    id: "pizza-map",
    title: "Show Pizza Map",
    templateUri: "ui://widget/pizza-map.html",
    invoking: "Hand-tossing a map",
    invoked: "Served a fresh map",
    html: `
<div id="pizzaz-root"></div>
<link rel="stylesheet" href="https://persistent.oaistatic.com/ecosystem-built-assets/pizzaz-0038.css">
<script type="module" src="https://persistent.oaistatic.com/ecosystem-built-assets/pizzaz-0038.js"></script>
    `.trim(),
    responseText: "Rendered a pizza map!",
    inputSchema: pizzaToolInputSchema,
  },
  {
    id: "pizza-carousel",
    title: "Show Pizza Carousel",
    templateUri: "ui://widget/pizza-carousel.html",
    invoking: "Carousel some spots",
    invoked: "Served a fresh carousel",
    html: `
<div id="pizzaz-carousel-root"></div>
<link rel="stylesheet" href="https://persistent.oaistatic.com/ecosystem-built-assets/pizzaz-carousel-0038.css">
<script type="module" src="https://persistent.oaistatic.com/ecosystem-built-assets/pizzaz-carousel-0038.js"></script>
    `.trim(),
    responseText: "Rendered a pizza carousel!",
    inputSchema: pizzaToolInputSchema,
  },
  {
    id: "pizza-albums",
    title: "Show Pizza Album",
    templateUri: "ui://widget/pizza-albums.html",
    invoking: "Hand-tossing an album",
    invoked: "Served a fresh album",
    html: `
<div id="pizzaz-albums-root"></div>
<link rel="stylesheet" href="https://persistent.oaistatic.com/ecosystem-built-assets/pizzaz-albums-0038.css">
<script type="module" src="https://persistent.oaistatic.com/ecosystem-built-assets/pizzaz-albums-0038.js"></script>
    `.trim(),
    responseText: "Rendered a pizza album!",
    inputSchema: pizzaToolInputSchema,
  },
  {
    id: "pizza-list",
    title: "Show Pizza List",
    templateUri: "ui://widget/pizza-list.html",
    invoking: "Hand-tossing a list",
    invoked: "Served a fresh list",
    html: `
<div id="pizzaz-list-root"></div>
<link rel="stylesheet" href="https://persistent.oaistatic.com/ecosystem-built-assets/pizzaz-list-0038.css">
<script type="module" src="https://persistent.oaistatic.com/ecosystem-built-assets/pizzaz-list-0038.js"></script>
    `.trim(),
    responseText: "Rendered a pizza list!",
    inputSchema: pizzaToolInputSchema,
  },
  {
    id: "pizza-video",
    title: "Show Pizza Video",
    templateUri: "ui://widget/pizza-video.html",
    invoking: "Hand-tossing a video",
    invoked: "Served a fresh video",
    html: `
<div id="pizzaz-video-root"></div>
<link rel="stylesheet" href="https://persistent.oaistatic.com/ecosystem-built-assets/pizzaz-video-0038.css">
<script type="module" src="https://persistent.oaistatic.com/ecosystem-built-assets/pizzaz-video-0038.js"></script>
    `.trim(),
    responseText: "Rendered a pizza video!",
    inputSchema: pizzaToolInputSchema,
  },
  {
    id: "insurance-state-selector",
    title: "Collect insurance state",
    templateUri: "ui://widget/insurance-state.html",
    invoking: "Collecting a customer's state",
    invoked: "Captured the customer's state",
    html: INSURANCE_STATE_WIDGET_HTML,
    responseText:
      "Let's confirm the customer's state before we continue with their insurance quote.",
    toolDescription:
      "Collects the customer's U.S. state so the assistant can surface insurance options that apply there.",
    inputSchema: insuranceStateInputSchema,
  },
];

const widgetsByUri = new Map<string, PizzazWidget>();

widgets.forEach((widget) => {
  widgetsByUri.set(widget.templateUri, widget);
});

const resources: Resource[] = widgets.map((widget) => ({
  uri: widget.templateUri,
  name: widget.title,
  description: `${widget.title} widget markup`,
  mimeType: "text/html+skybridge",
  _meta: widgetMeta(widget)
}));

const resourceTemplates: ResourceTemplate[] = widgets.map((widget) => ({
  uriTemplate: widget.templateUri,
  name: widget.title,
  description: `${widget.title} widget markup`,
  mimeType: "text/html+skybridge",
  _meta: widgetMeta(widget)
}));

type ToolHandlerResult = {
  structuredContent?: Record<string, unknown>;
  responseText?: string;
  content?: { type: "text"; text: string }[];
  meta?: Record<string, unknown>;
};

type ToolHandler = (args: unknown) => ToolHandlerResult | Promise<ToolHandlerResult>;

const toolHandlers = new Map<string, ToolHandler>();

const defaultPizzaToolHandler: ToolHandler = (args: unknown) => {
  const parsed = pizzaToolInputParser.parse(args ?? {});
  return {
    structuredContent: {
      pizzaTopping: parsed.pizzaTopping,
    },
  };
};

toolHandlers.set("insurance-state-selector", (args: unknown) => {
  const parsed = insuranceStateParser.parse(args ?? {});

  if (parsed.state) {
    return {
      structuredContent: { state: parsed.state },
      responseText: `Captured ${parsed.state} as the customer's state.`,
    };
  }

  return { structuredContent: {} };
});

type RegisteredTool = {
  tool: Tool;
  handler: ToolHandler;
  defaultResponseText: string;
  defaultMeta?: Record<string, unknown>;
};

const toolRegistry = new Map<string, RegisteredTool>();

function registerTool(definition: RegisteredTool) {
  toolRegistry.set(definition.tool.name, definition);
}

widgets.forEach((widget) => {
  const meta = widgetMeta(widget);
  registerTool({
    tool: {
      name: widget.id,
      description: widget.toolDescription ?? widget.title,
      inputSchema: widget.inputSchema,
      title: widget.title,
      _meta: meta,
    },
    handler: toolHandlers.get(widget.id) ?? defaultPizzaToolHandler,
    defaultResponseText: widget.responseText,
    defaultMeta: meta,
  });
});

const personalAutoProductsInputSchema = {
  type: "object",
  properties: {
    state: {
      type: "string",
      description:
        "Two-letter U.S. state or District of Columbia abbreviation (for example, \"CA\").",
      minLength: 2,
      maxLength: 2,
      pattern: "^[A-Za-z]{2}$",
    },
  },
  required: ["state"],
  additionalProperties: false,
} as const;

const personalAutoProductsInputParser = z
  .object({
    state: z
      .string()
      .trim()
      .min(2)
      .max(2)
      .regex(/^[A-Za-z]{2}$/)
      .transform((value) => value.toUpperCase()),
  })
  .strict();

const PERSONAL_AUTO_PRODUCTS_ENDPOINT =
  "https://gateway.pre.zrater.io/api/v1/linesOfBusiness/personalAuto/states";

async function fetchPersonalAutoProducts(
  args: unknown
): Promise<ToolHandlerResult> {
  const parsed = personalAutoProductsInputParser.parse(args ?? {});
  const state = parsed.state;

  const url = `${PERSONAL_AUTO_PRODUCTS_ENDPOINT}/${encodeURIComponent(
    state
  )}/activeProducts`;

  let response: Response;
  try {
    response = await fetch(url, {
      headers: {
        Accept: "application/json",
        Cookie: "BCSI-CS-7883f85839ae9af9=1",
        "User-Agent": "insomnia/11.1.0",
        "x-api-key": "e57528b0-95b4-4efe-8870-caa0f8a95143",
      },
    });
  } catch (error) {
    throw new Error(
      `Failed to fetch personal auto products: ${
        error instanceof Error ? error.message : String(error)
      }`
    );
  }

  if (response.status === 404) {
    return {
      structuredContent: {
        state,
        status: response.status,
        products: [],
      },
      responseText: `No active personal auto products found for ${state}.`,
    };
  }

  if (!response.ok) {
    throw new Error(
      `Personal auto products request failed with status ${response.status}`
    );
  }

  let rawBody = "";
  try {
    rawBody = await response.text();
  } catch (error) {
    throw new Error(
      `Failed to read personal auto products response: ${
        error instanceof Error ? error.message : String(error)
      }`
    );
  }

  let parsedBody: unknown = [];
  if (rawBody.trim().length > 0) {
    try {
      parsedBody = JSON.parse(rawBody);
    } catch (error) {
      throw new Error(
        `Failed to parse personal auto products response: ${
          error instanceof Error ? error.message : String(error)
        }`
      );
    }
  }

  const products = Array.isArray(parsedBody) ? parsedBody : [];
  const message = products.length
    ? `Found ${products.length} active personal auto product${
        products.length === 1 ? "" : "s"
      } for ${state}.`
    : `No active personal auto products found for ${state}.`;

  return {
    structuredContent: {
      state,
      status: response.status,
      products,
    },
    responseText: message,
  };
}

registerTool({
  tool: {
    name: "fetch-personal-auto-products",
    title: "Fetch personal auto products",
    description: "Retrieve active personal auto insurance products for a given state.",
    inputSchema: personalAutoProductsInputSchema,
  },
  handler: fetchPersonalAutoProducts,
  defaultResponseText: "Retrieved personal auto product availability.",
});

function createPizzazServer(): Server {
  const server = new Server(
    {
      name: "pizzaz-node",
      version: "0.1.0"
    },
    {
      capabilities: {
        resources: {},
        tools: {}
      }
    }
  );

  server.setRequestHandler(ListResourcesRequestSchema, async (_request: ListResourcesRequest) => ({
    resources
  }));

  server.setRequestHandler(ReadResourceRequestSchema, async (request: ReadResourceRequest) => {
    const widget = widgetsByUri.get(request.params.uri);

    if (!widget) {
      throw new Error(`Unknown resource: ${request.params.uri}`);
    }

    return {
      contents: [
        {
          uri: widget.templateUri,
          mimeType: "text/html+skybridge",
          text: widget.html,
          _meta: widgetMeta(widget)
        }
      ]
    };
  });

  server.setRequestHandler(ListResourceTemplatesRequestSchema, async (_request: ListResourceTemplatesRequest) => ({
    resourceTemplates
  }));

  server.setRequestHandler(ListToolsRequestSchema, async (_request: ListToolsRequest) => ({
    tools: Array.from(toolRegistry.values()).map((entry) => entry.tool),
  }));

  server.setRequestHandler(CallToolRequestSchema, async (request: CallToolRequest) => {
    const registration = toolRegistry.get(request.params.name);

    if (!registration) {
      throw new Error(`Unknown tool: ${request.params.name}`);
    }

    const handlerResult = await registration.handler(request.params.arguments ?? {});
    const structuredContent = handlerResult?.structuredContent ?? {};
    const responseText = handlerResult?.responseText ?? registration.defaultResponseText;
    const content = handlerResult?.content ?? [
      {
        type: "text" as const,
        text: responseText,
      },
    ];
    const meta = handlerResult?.meta ?? registration.defaultMeta;

    const response: {
      content: typeof content;
      structuredContent: typeof structuredContent;
      _meta?: Record<string, unknown>;
    } = {
      content,
      structuredContent,
    };

    if (meta) {
      response._meta = meta;
    }

    return response;
  });

  return server;
}

type SessionRecord = {
  server: Server;
  transport: SSEServerTransport;
};

const sessions = new Map<string, SessionRecord>();

const ssePath = "/mcp";
const postPath = "/mcp/messages";

async function handleSseRequest(res: ServerResponse) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  const server = createPizzazServer();
  const transport = new SSEServerTransport(postPath, res);
  const sessionId = transport.sessionId;

  sessions.set(sessionId, { server, transport });

  transport.onclose = async () => {
    sessions.delete(sessionId);
    await server.close();
  };

  transport.onerror = (error) => {
    console.error("SSE transport error", error);
  };

  try {
    await server.connect(transport);
  } catch (error) {
    sessions.delete(sessionId);
    console.error("Failed to start SSE session", error);
    if (!res.headersSent) {
      res.writeHead(500).end("Failed to establish SSE connection");
    }
  }
}

async function handlePostMessage(
  req: IncomingMessage,
  res: ServerResponse,
  url: URL
) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Headers", "content-type");
  const sessionId = url.searchParams.get("sessionId");

  if (!sessionId) {
    res.writeHead(400).end("Missing sessionId query parameter");
    return;
  }

  const session = sessions.get(sessionId);

  if (!session) {
    res.writeHead(404).end("Unknown session");
    return;
  }

  try {
    await session.transport.handlePostMessage(req, res);
  } catch (error) {
    console.error("Failed to process message", error);
    if (!res.headersSent) {
      res.writeHead(500).end("Failed to process message");
    }
  }
}

const portEnv = Number(process.env.PORT ?? 8000);
const port = Number.isFinite(portEnv) ? portEnv : 8000;

const httpServer = createServer(async (req: IncomingMessage, res: ServerResponse) => {
  if (!req.url) {
    res.writeHead(400).end("Missing URL");
    return;
  }

  const url = new URL(req.url, `http://${req.headers.host ?? "localhost"}`);

  if (req.method === "OPTIONS" && (url.pathname === ssePath || url.pathname === postPath)) {
    res.writeHead(204, {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "content-type"
    });
    res.end();
    return;
  }

  if (req.method === "GET" && url.pathname === ssePath) {
    await handleSseRequest(res);
    return;
  }

  if (req.method === "POST" && url.pathname === postPath) {
    await handlePostMessage(req, res, url);
    return;
  }

  res.writeHead(404).end("Not Found");
});

httpServer.on("clientError", (err: Error, socket) => {
  console.error("HTTP client error", err);
  socket.end("HTTP/1.1 400 Bad Request\r\n\r\n");
});

httpServer.listen(port, () => {
  console.log(`Pizzaz MCP server listening on http://localhost:${port}`);
  console.log(`  SSE stream: GET http://localhost:${port}${ssePath}`);
  console.log(`  Message post endpoint: POST http://localhost:${port}${postPath}?sessionId=...`);
});
