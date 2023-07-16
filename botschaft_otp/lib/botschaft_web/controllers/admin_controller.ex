defmodule BotschaftWeb.AdminController do
  use BotschaftWeb, :controller

  def home(conn, _params) do
    # The home page is often custom made,
    # so skip the default app layout.
    destinations = Botschaft.Config.get_destinations()
    render(conn, :home, destinations: destinations)
  end

  def denied(conn, _params) do
    render(conn, :login)
  end

  def send_message(conn, %{"destination" => destination, "message" => message}) do
    [provider, destination] = String.split(destination, ".", parts: 2)
    IO.puts "got #{destination}: #{message}"
    # TODO: get provider module by name and send message
    case Botschaft.Providers.send_message(provider, destination, message) do
      {:error, reason} ->
        IO.puts "failed to send message: #{reason}"
        put_flash(conn, :error, "Failed to send message!")
      _ ->
        put_flash(conn, :info, "Message sent!")
    end
    |> redirect(to: "/admin")
  end
end
