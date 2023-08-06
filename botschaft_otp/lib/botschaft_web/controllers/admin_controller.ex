defmodule BotschaftWeb.AdminController do
  use BotschaftWeb, :controller

  def home(conn, _params) do
    # The home page is often custom made,
    # so skip the default app layout.
    destinations = for {provider, dests} <- Botschaft.Config.get_all_providers(), into: %{} do
      dest_names = Map.keys(dests)
      {provider, dest_names}
    end
    render(conn, :home, destinations: destinations)
  end

  def denied(conn, _params) do
    render(conn, :login)
  end

  def login(conn, %{"admin_token" => admin_token_input}) do
    IO.puts "admin login!"
    case Botschaft.Config.admin() do
      {:ok, %{"bearer_token" => admin_token}} = c ->
        IO.puts "auth required: #{inspect c}"
        if admin_token_input == admin_token do
            IO.puts "admin authenticated!"
            conn
            |> put_session(:admin, true)
        else
          conn
        end
      _ -> conn
    end
    |> redirect(to: "/admin")
  end

  def send_message(conn, %{"destination" => destination, "message" => message}) when is_binary(message) do
    [provider, destination] = String.split(destination, ".", parts: 2)
    IO.puts "got #{destination}: #{message}"
    # TODO: get provider module by name and send message
    case Botschaft.Providers.send_message(provider, destination, Botschaft.Message.text(message)) do
      {:error, reason} ->
        IO.puts "failed to send message: #{reason}"
        put_flash(conn, :error, "Failed to send message!")
      _ ->
        put_flash(conn, :info, "Message sent!")
    end
    |> redirect(to: "/admin")
  end

  def send_message(conn, %{"topic" => topic, "message" => message}) when is_binary(message) do
    IO.puts "got topic #{topic}: #{message}"
    # TODO: get provider module by name and send message
    case Botschaft.Topics.send(topic, Botschaft.Message.text(message)) do
      {:error, reason} ->
        IO.puts "failed to send message: #{reason}"
        put_flash(conn, :error, "Failed to send message!")
      _ ->
        put_flash(conn, :info, "Message sent!")
    end
    |> redirect(to: "/admin")
  end
end
