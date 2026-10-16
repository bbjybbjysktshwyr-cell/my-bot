-- Steal An Egg - Smooth Teleport Hub
local Players = game:GetService("Players")
local CoreGui = game:GetService("CoreGui")
local LocalPlayer = Players.LocalPlayer

if CoreGui:FindFirstChild("EggHubGui") then
    CoreGui.EggHubGui:Destroy()
end

local ScreenGui = Instance.new("ScreenGui")
ScreenGui.Name = "EggHubGui"
pcall(function() ScreenGui.Parent = CoreGui end)
if not ScreenGui.Parent then ScreenGui.Parent = LocalPlayer:WaitForChild("PlayerGui") end
ScreenGui.ResetOnSpawn = false

-- النافذة الرئيسية
local MainFrame = Instance.new("Frame")
MainFrame.Parent = ScreenGui
MainFrame.BackgroundColor3 = Color3.fromRGB(20, 20, 25)
MainFrame.Position = UDim2.new(0.25, 0, 0.15, 0)
MainFrame.Size = UDim2.new(0, 280, 0, 390)
MainFrame.Active = true
MainFrame.Draggable = true

local Title = Instance.new("TextLabel")
Title.Parent = MainFrame
Title.BackgroundColor3 = Color3.fromRGB(10, 10, 15)
Title.Size = UDim2.new(1, 0, 0, 40)
Title.Text = "Worlds Teleport Hub 🚀"
Title.TextColor3 = Color3.fromRGB(255, 255, 255)
Title.TextSize = 16
Title.Font = Enum.Font.SourceSansBold

-- دالة انتقال سريعة وناعمة بدون أي كلج أو تعليق أو رسيبون
local function smoothTeleport(targetCFrame)
    local char = LocalPlayer.Character
    if char and char:FindFirstChild("HumanoidRootPart") then
        local root = char.HumanoidRootPart
        -- إيقاف القصور الذاتي والسرعة المفاجئة لمنع التعليق
        root.AssemblyLinearVelocity = Vector3.new(0, 0, 0)
        root.AssemblyAngularVelocity = Vector3.new(0, 0, 0)
        root.CFrame = targetCFrame
    end
end

-- زر العودة للبداية / القاعدة (بدون رسيبون وشغال 100% وبدون تعليق)
local SpawnBtn = Instance.new("TextButton")
SpawnBtn.Parent = MainFrame
SpawnBtn.BackgroundColor3 = Color3.fromRGB(50, 120, 200)
SpawnBtn.Position = UDim2.new(0.1, 0, 0.15, 0)
SpawnBtn.Size = UDim2.new(0.8, 0, 0, 40)
SpawnBtn.Text = "العودة للبداية / القاعدة 🛡️"
SpawnBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
SpawnBtn.TextSize = 14
SpawnBtn.Font = Enum.Font.SourceSansBold

SpawnBtn.MouseButton1Click:Connect(function()
    local spawnPart = workspace:FindFirstChild("SpawnLocation") or workspace:FindFirstChild("Spawn")
    if spawnPart then
        smoothTeleport(spawnPart.CFrame + Vector3.new(0, 3, 0))
    else
        smoothTeleport(CFrame.new(0, 10, 0))
    end
end)

-- قائمة العوالم والمراحل
local worldList = {
    "Forest",
    "Lake",
    "Desert",
    "Jungle",
    "Snow",
    "Volcano",
    "Abyss Ocean",
    "Prehistoric",
    "Cosmic",
    "Cherry Blossom",
    "Titan Temple",
    "Demons",
    "Enchanted Forest"
}

local selectedWorld = "Forest"

local DropdownBtn = Instance.new("TextButton")
DropdownBtn.Parent = MainFrame
DropdownBtn.BackgroundColor3 = Color3.fromRGB(35, 35, 45)
DropdownBtn.Position = UDim2.new(0.1, 0, 0.32, 0)
DropdownBtn.Size = UDim2.new(0.8, 0, 0, 35)
DropdownBtn.Text = "اختر المرحلة: " .. selectedWorld .. " ▼"
DropdownBtn.TextColor3 = Color3.fromRGB(0, 255, 150)
DropdownBtn.TextSize = 13
DropdownBtn.Font = Enum.Font.SourceSansBold

local DropdownList = Instance.new("ScrollingFrame")
DropdownList.Parent = MainFrame
DropdownList.BackgroundColor3 = Color3.fromRGB(28, 28, 38)
DropdownList.Position = UDim2.new(0.1, 0, 0.44, 0)
DropdownList.Size = UDim2.new(0.8, 0, 0, 170)
DropdownList.Visible = false
DropdownList.CanvasSize = UDim2.new(0, 0, 3.5, 0)
DropdownList.ScrollBarThickness = 6

local UIListLayout = Instance.new("UIListLayout")
UIListLayout.Parent = DropdownList
UIListLayout.SortOrder = Enum.SortOrder.LayoutOrder

for _, wName in ipairs(worldList) do
    local opt = Instance.new("TextButton")
    opt.Parent = DropdownList
    opt.Size = UDim2.new(1, 0, 0, 30)
    opt.BackgroundColor3 = Color3.fromRGB(40, 40, 50)
    opt.Text = wName
    opt.TextColor3 = Color3.fromRGB(255, 255, 255)
    opt.TextSize = 13
    opt.Font = Enum.Font.SourceSans
    
    opt.MouseButton1Click:Connect(function()
        selectedWorld = wName
        DropdownBtn.Text = "اختر المرحلة: " .. wName .. " ▼"
        DropdownList.Visible = false
    end)
end

DropdownBtn.MouseButton1Click:Connect(function()
    DropdownList.Visible = not DropdownList.Visible
end)

-- زر الانتقال الفوري للمرحلة بدون كلج
local TeleportWorldBtn = Instance.new("TextButton")
TeleportWorldBtn.Parent = MainFrame
TeleportWorldBtn.BackgroundColor3 = Color3.fromRGB(80, 180, 80)
TeleportWorldBtn.Position = UDim2.new(0.1, 0, 0.82, 0)
TeleportWorldBtn.Size = UDim2.new(0.8, 0, 0, 42)
TeleportWorldBtn.Text = "الانتقال للمرحلة المحددة ⚡"
TeleportWorldBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
TeleportWorldBtn.TextSize = 14
TeleportWorldBtn.Font = Enum.Font.SourceSansBold

TeleportWorldBtn.MouseButton1Click:Connect(function()
    local targetPosition = nil
    
    for _, v in ipairs(workspace:GetDescendants()) do
        if (v:IsA("TextLabel") and v.Text:lower():find(selectedWorld:lower())) or (v.Name:lower() == selectedWorld:lower()) then
            local parentPart = v:FindFirstAncestorWhichIsA("BasePart") or v.Parent
            if parentPart and parentPart:IsA("BasePart") then
                targetPosition = parentPart.CFrame
                break
            elseif v:IsA("BasePart") then
                targetPosition = v.CFrame
                break
            end
        end
    end
    
    if targetPosition then
        smoothTeleport(targetPosition + Vector3.new(0, 4, 0))
    else
        local char = LocalPlayer.Character
        if char and char:FindFirstChild("HumanoidRootPart") then
            smoothTeleport(char.HumanoidRootPart.CFrame + Vector3.new(0, 0, -80))
        end
    end
end)
