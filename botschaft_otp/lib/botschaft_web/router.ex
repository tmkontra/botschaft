defmodule BotschaftWeb.Router do
  use BotschaftWeb, :router

  pipeline :browser do
    plug :accepts, ["html"]
    plug :fetch_session
    plug :fetch_live_flash
    plug :put_root_layout, html: {BotschaftWeb.Layouts, :root}
    plug :protect_from_forgery
    plug :put_secure_browser_headers
    plug :authenticate
  end

  pipeline :api do
    plug :accepts, ["json"]
    plug :authenticate
  end

  pipeline :admin do
    plug :require_admin, :denied
  end

  defp authenticate(conn, _opts) do
    # admin already logged in
    case get_session(conn, :admin) do
      nil ->
        # check headers if auth is required
        case Botschaft.Config.require_auth do
          {:required, %{admin: admin_token, user: user_token}} = c ->
            IO.puts "auth required: #{inspect c}"
            case get_req_header(conn, "authorization") do
              ["Bearer " <> ^admin_token] ->
                conn
                |> assign(:admin, true)
                |> assign(:authenticated, true)
              ["Bearer " <> ^user_token] ->
                conn
                |> assign(:authenticated, true)
              _ -> conn
            end
          _ ->
            IO.puts "no auth required"
            conn
            |> assign(:admin, true)
            |> assign(:authenticated, true)
        end
      _ -> conn
      |> assign(:admin, true)
      |> assign(:authenticated, true)
    end
  end

  defp require_admin(conn, denied) do
    if conn.assigns[:admin] do
      conn
    else
      conn
      |> put_flash(:error, "You are not authorized to access this page.")
      |> redirect(to: BotschaftWeb.Router.Helpers.admin_path(conn, denied))
      |> halt()
    end
  end

  scope "/", BotschaftWeb do
    pipe_through :browser

    get "/", IndexController, :index

    scope "/admin" do
      get "/auth", AdminController, :denied

      scope "" do
        pipe_through :admin

        get "/", AdminController, :home

        post "/auth", AdminController, :login

        post "/message", AdminController, :send_message
      end
    end
  end

  # Other scopes may use custom stacks.
  # scope "/api", BotschaftWeb do
  #   pipe_through :api
  # end

  # Enable LiveDashboard and Swoosh mailbox preview in development
  if Application.compile_env(:botschaft, :dev_routes) do
    # If you want to use the LiveDashboard in production, you should put
    # it behind authentication and allow only admins to access it.
    # If your application does not have an admins-only section yet,
    # you can use Plug.BasicAuth to set up some basic authentication
    # as long as you are also using SSL (which you should anyway).
    import Phoenix.LiveDashboard.Router

    scope "/dev" do
      pipe_through :browser

      live_dashboard "/dashboard", metrics: BotschaftWeb.Telemetry
      forward "/mailbox", Plug.Swoosh.MailboxPreview
    end
  end
end
