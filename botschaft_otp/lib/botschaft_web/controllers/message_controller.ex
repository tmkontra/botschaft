defmodule BotschaftWeb.MessageController do
  use BotschaftWeb, :controller

  def send_to_topic(conn, %{"topic" => topic_name}) do
    message = "hardcode topic message"
    IO.puts("got topic #{topic_name}: #{message}")
    # TODO: get provider module by name and send message
    case Botschaft.Topics.send(topic_name, Botschaft.Message.text(message)) do
      {:error, reason} ->
        IO.puts("failed to send message: #{reason}")

        conn
        |> send_resp(500, "")

      _ ->
        conn
        |> send_resp(201, "")
    end
  end

  def send_to_provider(conn, %{"provider" => provider_name, "destination" => destination_name}) do
    message = "hardcode message"

    case Botschaft.Providers.send_message(
           provider_name,
           destination_name,
           Botschaft.Message.text(message)
         ) do
      {:error, reason} ->
        IO.puts("failed to send message: #{reason}")

        conn
        |> send_resp(500, "")

      _ ->
        conn
        |> send_resp(201, "")
    end
  end
end
